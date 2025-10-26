"""
Atlas 3+3 - Dashboard Page
Interactive dashboard with KPIs, filters, map, charts, and project table
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import json
from typing import Dict, List, Any, Optional

from src.database import AtlasDB
from src.constants import (
    APP_NAME, UIA_REGIONS, SDGS, SESSION_KEYS, CHART_COLORS,
    MAP_MARKER_SETTINGS, DEFAULT_MAP_CENTER, CHART_DEFAULTS
)
from src.utils import (
    format_currency, format_large_number, get_export_filename,
    export_to_csv, export_to_xlsx, get_color_for_status,
    get_color_for_sdg, truncate_text, get_map_bounds,
    get_session_value, set_session_value
)

# Initialize database using new interface
@st.cache_resource
def get_database():
    from src.database_interface import get_cached_database
    return get_cached_database()

def render_kpi_widgets(filtered_projects: List[Dict[str, Any]]):
    """Render 5 KPI widgets in header"""
    if not filtered_projects:
        projects_df = pd.DataFrame()
    else:
        projects_df = pd.DataFrame(filtered_projects)

    # Calculate metrics
    total_projects = len(projects_df)
    total_cities = projects_df['city'].nunique() if not projects_df.empty else 0
    total_countries = projects_df['country'].nunique() if not projects_df.empty else 0

    if not projects_df.empty:
        funding_needed = projects_df['funding_needed_usd'].fillna(0).sum()
        funding_spent = projects_df[projects_df['project_status'] == 'Implemented']['funding_needed_usd'].fillna(0).sum()
    else:
        funding_needed = 0
        funding_spent = 0

    # Display KPIs
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="📊 Total Projects",
            value=format_large_number(total_projects),
            delta=None
        )

    with col2:
        st.metric(
            label="🏙️ Cities",
            value=format_large_number(total_cities),
            delta=None
        )

    with col3:
        st.metric(
            label="🌍 Countries",
            value=format_large_number(total_countries),
            delta=None
        )

    with col4:
        st.metric(
            label="💰 Funding Needed",
            value=format_currency(funding_needed).replace("$", "$" if funding_needed < 1000000 else "$") + ("M" if funding_needed >= 1000000 else ""),
            delta=None
        )

    with col5:
        st.metric(
            label="✅ Funding Spent",
            value=format_currency(funding_spent).replace("$", "$" if funding_spent < 1000000 else "$") + ("M" if funding_spent >= 1000000 else ""),
            delta=None
        )

def render_filter_bar(db) -> Dict[str, Any]:
    """Render filter controls and return selected filters"""
    st.subheader("🔍 Filters")

    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])

    with col1:
        region_options = ["All Regions"] + list(UIA_REGIONS.values())
        selected_region = st.selectbox("UIA Region", region_options, key="region_filter")

    with col2:
        sdg_options = ["All SDGs"] + [f"{k}. {v['name']}" for k, v in SDGS.items()]
        selected_sdg = st.selectbox("SDG", sdg_options, key="sdg_filter")

    with col3:
        cities = db.get_unique_cities()
        city_options = ["All Cities"] + cities
        selected_city = st.selectbox("City", city_options, key="city_filter")

    with col4:
        organizations = db.get_unique_organizations()
        org_options = ["All Organizations"] + organizations
        selected_org = st.selectbox("Funded by", org_options, key="org_filter")

    with col5:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        if st.button("🗑️ Clear Filters", use_container_width=True):
            st.session_state.region_filter = "All Regions"
            st.session_state.sdg_filter = "All SDGs"
            st.session_state.city_filter = "All Cities"
            st.session_state.org_filter = "All Organizations"
            st.rerun()

    # Advanced geospatial filters (if PostgreSQL database supports it)
    with st.expander("🗺️ Advanced Location Filters", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Find projects near location:**")
            search_lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=0.0, step=0.1, key="search_lat")
            search_lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=0.0, step=0.1, key="search_lon")
            search_radius = st.slider("Search radius (km)", min_value=1, max_value=500, value=50, key="search_radius")

            use_location_filter = st.checkbox("Enable location-based search", key="use_location")

        with col2:
            st.markdown("**Or search by bounding box:**")
            north = st.number_input("North latitude", min_value=-90.0, max_value=90.0, value=90.0, step=0.1, key="bound_north")
            south = st.number_input("South latitude", min_value=-90.0, max_value=90.0, value=-90.0, step=0.1, key="bound_south")
            east = st.number_input("East longitude", min_value=-180.0, max_value=180.0, value=180.0, step=0.1, key="bound_east")
            west = st.number_input("West longitude", min_value=-180.0, max_value=180.0, value=-180.0, step=0.1, key="bound_west")

            use_bounds_filter = st.checkbox("Enable bounds-based search", key="use_bounds")

    # Convert selections to filter parameters
    filters = {}

    if selected_region != "All Regions":
        filters['region'] = selected_region

    if selected_sdg != "All SDGs":
        sdg_id = int(selected_sdg.split(".")[0])
        filters['sdg'] = sdg_id

    if selected_city != "All Cities":
        filters['city'] = selected_city

    if selected_org != "All Organizations":
        filters['funded_by'] = selected_org

    # Add geospatial filters if enabled
    if use_location_filter and (search_lat != 0.0 or search_lon != 0.0):
        filters['near_lat'] = search_lat
        filters['near_lon'] = search_lon
        filters['radius_km'] = search_radius

    if use_bounds_filter and not (north == 90 and south == -90 and east == 180 and west == -180):
        if north > south and east > west:  # Basic validation
            filters['bounds'] = [north, south, east, west]

    return filters

def render_export_buttons(projects_df: pd.DataFrame):
    """Render export buttons for filtered data"""
    if projects_df.empty:
        return

    col1, col2, col3 = st.columns([1, 1, 8])

    # Prepare export data
    export_df = projects_df[[
        'project_name', 'city', 'country', 'region_name',
        'project_status', 'funding_needed_usd', 'organization_name'
    ]].copy()
    export_df.columns = [
        'Project Name', 'City', 'Country', 'UIA Region',
        'Status', 'Funding Needed (USD)', 'Organization'
    ]

    with col1:
        csv_data = export_to_csv(export_df)
        st.download_button(
            label="📄 Export CSV",
            data=csv_data,
            file_name=get_export_filename("csv"),
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        xlsx_data = export_to_xlsx(export_df)
        st.download_button(
            label="📊 Export XLSX",
            data=xlsx_data,
            file_name=get_export_filename("xlsx"),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

def render_map(projects: List[Dict[str, Any]]):
    """Render Folium map with project markers"""
    if not projects:
        st.info("No projects to display on map")
        return None

    projects_df = pd.DataFrame(projects)

    # Filter projects with coordinates
    map_projects = projects_df.dropna(subset=['latitude', 'longitude'])

    if map_projects.empty:
        st.info("No projects have coordinate data for map display")
        return None

    # Calculate map bounds
    bounds = get_map_bounds(map_projects.to_dict('records'))

    # Create map
    if bounds:
        center_lat = (bounds[0][0] + bounds[1][0]) / 2
        center_lon = (bounds[0][1] + bounds[1][1]) / 2
        zoom = 3
    else:
        center_lat, center_lon = DEFAULT_MAP_CENTER
        zoom = 2

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="OpenStreetMap"
    )

    # Add markers
    for _, project in map_projects.iterrows():
        status = project['project_status']
        marker_settings = MAP_MARKER_SETTINGS.get(status, MAP_MARKER_SETTINGS['default'])

        popup_html = f"""
        <div style="width: 250px;">
            <h4>{project['project_name']}</h4>
            <p><strong>Location:</strong> {project['city']}, {project['country']}</p>
            <p><strong>Status:</strong> {project['project_status']}</p>
            <p><strong>Funding:</strong> {format_currency(project['funding_needed_usd']) if pd.notna(project['funding_needed_usd']) else 'Not specified'}</p>
            <p><strong>Organization:</strong> {project['organization_name']}</p>
        </div>
        """

        folium.Marker(
            location=[project['latitude'], project['longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=project['project_name'],
            icon=folium.Icon(
                color=marker_settings['color'],
                icon=marker_settings['icon']
            )
        ).add_to(m)

    # Fit map to bounds if available
    if bounds:
        m.fit_bounds(bounds, padding=[20, 20])

    # Display map and capture interactions
    map_data = st_folium(m, width=700, height=500, returned_objects=["last_object_clicked"])

    return map_data

def render_analytics_charts(projects: List[Dict[str, Any]]):
    """Render 6 analytical charts"""
    if not projects:
        st.info("No data available for charts")
        return

    projects_df = pd.DataFrame(projects)

    # Chart 1: SDG Distribution
    st.subheader("📊 SDG Distribution")

    # Get SDG data from database
    db = get_database()
    sdg_data = []
    for project in projects:
        project_detail = db.get_project_by_id(project['id'])
        if project_detail and project_detail.get('sdgs'):
            for sdg in project_detail['sdgs']:
                sdg_data.append({
                    'project_id': project['id'],
                    'sdg_id': sdg['id'],
                    'sdg_name': f"{sdg['id']}. {sdg['name']}",
                    'funding': project.get('funding_needed_usd', 0) or 0
                })

    if sdg_data:
        sdg_df = pd.DataFrame(sdg_data)
        sdg_counts = sdg_df.groupby('sdg_name').size().reset_index(name='count')
        sdg_counts = sdg_counts.sort_values('count', ascending=True)

        fig1 = px.bar(
            sdg_counts.tail(10),  # Top 10
            x='count',
            y='sdg_name',
            orientation='h',
            title="Projects by SDG",
            color='count',
            color_continuous_scale='Blues'
        )
        fig1.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

        # Chart 2: Top 3 Most Used SDGs
        st.subheader("🥇 Top 3 Most Used SDGs")
        top_3_sdgs = sdg_counts.tail(3)

        fig2 = px.bar(
            top_3_sdgs,
            x='sdg_name',
            y='count',
            title="Most Popular SDGs",
            color='count',
            color_continuous_scale='Greens'
        )
        fig2.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

        # Chart 3: Top 3 SDGs by Funding
        st.subheader("💰 Top 3 SDGs by Funding Need")
        sdg_funding = sdg_df.groupby('sdg_name')['funding'].sum().reset_index()
        sdg_funding = sdg_funding.sort_values('funding', ascending=True).tail(3)

        fig3 = px.bar(
            sdg_funding,
            x='sdg_name',
            y='funding',
            title="SDGs by Total Funding Needed",
            color='funding',
            color_continuous_scale='Oranges'
        )
        fig3.update_layout(height=400, showlegend=False)
        fig3.update_yaxis(title="Funding Needed (USD)")
        st.plotly_chart(fig3, use_container_width=True)

    # Chart 4: Projects by Region
    st.subheader("🌍 Projects by Region")
    region_counts = projects_df.groupby('region_name').size().reset_index(name='count')

    fig4 = px.pie(
        region_counts,
        values='count',
        names='region_name',
        title="Regional Distribution"
    )
    fig4.update_layout(height=400)
    st.plotly_chart(fig4, use_container_width=True)

    # Chart 5: Funding Needed by Region
    st.subheader("💸 Funding Needed by Region")
    region_funding = projects_df.groupby('region_name')['funding_needed_usd'].sum().fillna(0).reset_index()

    fig5 = px.bar(
        region_funding,
        x='region_name',
        y='funding_needed_usd',
        title="Total Funding Needed by Region",
        color='funding_needed_usd',
        color_continuous_scale='Reds'
    )
    fig5.update_layout(height=400, showlegend=False)
    fig5.update_xaxis(title="UIA Region")
    fig5.update_yaxis(title="Funding Needed (USD)")
    st.plotly_chart(fig5, use_container_width=True)

    # Chart 6: Project Status Distribution
    st.subheader("📈 Project Status Distribution")
    status_counts = projects_df.groupby('project_status').size().reset_index(name='count')

    colors = [get_color_for_status(status) for status in status_counts['project_status']]

    fig6 = px.bar(
        status_counts,
        x='project_status',
        y='count',
        title="Projects by Implementation Status",
        color='project_status',
        color_discrete_map={
            status: get_color_for_status(status)
            for status in status_counts['project_status']
        }
    )
    fig6.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig6, use_container_width=True)

def render_projects_table(projects: List[Dict[str, Any]], db):
    """Render sortable projects table with pagination and full-text search"""
    if not projects:
        st.info("No projects match your current filters")
        return

    projects_df = pd.DataFrame(projects)

    st.subheader(f"📋 Projects Overview ({len(projects)} projects)")

    # Search controls
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

    with col1:
        search_term = st.text_input("🔍 Search projects", placeholder="Enter keywords for full-text search...")

    with col2:
        if st.button("🔍 Full-Text Search", help="Use PostgreSQL full-text search (if available)"):
            if search_term and hasattr(db, 'search_projects'):
                try:
                    search_results = db.search_projects(search_term, limit=100)
                    if search_results:
                        projects_df = pd.DataFrame(search_results)
                        st.success(f"Found {len(search_results)} projects matching '{search_term}'")
                    else:
                        st.warning(f"No projects found matching '{search_term}'")
                except Exception as e:
                    st.error(f"Full-text search error: {e}")

    with col3:
        sort_by = st.selectbox("Sort by", ["project_name", "city", "funding_needed_usd", "project_status"])

    with col4:
        sort_order = st.selectbox("Order", ["Ascending", "Descending"])

    # Apply search filter
    if search_term:
        mask = (
            projects_df['project_name'].str.contains(search_term, case=False, na=False) |
            projects_df['organization_name'].str.contains(search_term, case=False, na=False)
        )
        projects_df = projects_df[mask]

    # Apply sorting
    ascending = sort_order == "Ascending"
    projects_df = projects_df.sort_values(sort_by, ascending=ascending)

    # Pagination
    items_per_page = 10
    total_items = len(projects_df)
    total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)

    page = st.selectbox("Page", range(1, total_pages + 1), format_func=lambda x: f"Page {x} of {total_pages}")

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_df = projects_df.iloc[start_idx:end_idx]

    # Display table
    if not page_df.empty:
        # Format table data
        display_df = page_df.copy()
        display_df['funding_display'] = display_df['funding_needed_usd'].apply(
            lambda x: format_currency(x) if pd.notna(x) else "Not specified"
        )

        # Select columns for display
        table_df = display_df[[
            'project_name', 'city', 'country', 'region_name',
            'project_status', 'funding_display', 'organization_name'
        ]].copy()

        table_df.columns = [
            'Project Name', 'City', 'Country', 'UIA Region',
            'Status', 'Funding Needed', 'Organization'
        ]

        # Display table with click handling
        event = st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        # Handle row selection
        if event.selection.rows:
            selected_idx = event.selection.rows[0]
            selected_project_id = page_df.iloc[selected_idx]['id']
            set_session_value("selected_project_id", selected_project_id)
            set_session_value("show_drawer", True)
            st.rerun()

    else:
        st.info("No projects found matching your search criteria")

def render_project_drawer():
    """Render project detail drawer when a project is selected"""
    project_id = get_session_value("selected_project_id")
    show_drawer = get_session_value("show_drawer", False)

    if not show_drawer or not project_id:
        return

    db = get_database()
    project = db.get_project_by_id(project_id)

    if not project:
        st.error("Project not found")
        set_session_value("show_drawer", False)
        return

    # Drawer header with close button
    col1, col2 = st.columns([10, 1])
    with col1:
        st.subheader(f"📄 {project['project_name']}")
    with col2:
        if st.button("✖️", help="Close", key="close_drawer"):
            set_session_value("show_drawer", False)
            st.rerun()

    # Project details
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**📍 Location:** {project['city']}, {project['country']}")
        st.markdown(f"**🌍 UIA Region:** {project['region_name']}")
        st.markdown(f"**📊 Status:** {project['project_status']}")

    with col2:
        funding = format_currency(project['funding_needed_usd']) if project['funding_needed_usd'] else "Not specified"
        st.markdown(f"**💰 Funding Needed:** {funding}")
        st.markdown(f"**🏢 Organization:** {project['organization_name']}")
        st.markdown(f"**👤 Contact:** {project['contact_person']}")

    # Images
    if project.get('images'):
        st.markdown("**📸 Project Images:**")
        for img in project['images']:
            if img['image_url']:
                try:
                    st.image(img['image_url'], caption=img.get('alt_text', ''), use_column_width=True)
                except:
                    st.error(f"Could not load image: {img['image_url']}")

    # Descriptions
    st.markdown("**📝 Brief Description:**")
    st.write(project['brief_description'])

    st.markdown("**📋 Detailed Description:**")
    st.write(project['detailed_description'])

    if project.get('success_factors'):
        st.markdown("**🎯 Success Factors:**")
        st.write(project['success_factors'])

    # SDGs
    if project.get('sdgs'):
        st.markdown("**🎯 Sustainable Development Goals:**")
        sdg_html = ""
        for sdg in project['sdgs']:
            color = sdg['color']
            sdg_html += f'<span style="background-color: {color}; color: white; padding: 4px 8px; border-radius: 4px; margin: 2px; display: inline-block; font-size: 0.8em;">{sdg["id"]}. {sdg["name"]}</span> '
        st.markdown(sdg_html, unsafe_allow_html=True)

    # Typologies
    if project.get('typologies'):
        st.markdown("**🏗️ Project Typologies:**")
        for typology in project['typologies']:
            st.markdown(f"- {typology['typology']}")

    # Requirements
    if project.get('requirements'):
        st.markdown("**✅ Key Requirements:**")
        requirements_by_category = {}
        for req in project['requirements']:
            category = req['requirement_category']
            if category not in requirements_by_category:
                requirements_by_category[category] = []
            requirements_by_category[category].append(req['requirement_text'])

        for category, reqs in requirements_by_category.items():
            st.markdown(f"*{category}:*")
            for req in reqs:
                st.markdown(f"  - {req}")

def main():
    """Main dashboard function"""
    # Page configuration
    st.set_page_config(
        page_title=f"{APP_NAME} - Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("📊 Atlas 3+3 Dashboard")
    st.markdown("Explore sustainable development projects from around the world")

    # Initialize database
    db = get_database()

    # Render filters and get selected criteria
    filters = render_filter_bar(db)

    # Get filtered projects
    if filters:
        filtered_projects = db.get_projects_by_filters(**filters)
    else:
        filtered_projects = db.get_all_published_projects()

    # Render KPI widgets
    render_kpi_widgets(filtered_projects)

    st.markdown("---")

    # Export buttons
    if filtered_projects:
        render_export_buttons(pd.DataFrame(filtered_projects))

    # Main content layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🗺️ Project Locations")
        map_data = render_map(filtered_projects)

    with col2:
        st.subheader("📈 Analytics")
        render_analytics_charts(filtered_projects)

    st.markdown("---")

    # Projects table
    render_projects_table(filtered_projects, db)

    # Project detail drawer (shown as expander at bottom)
    if get_session_value("show_drawer", False):
        with st.expander("📄 Project Details", expanded=True):
            render_project_drawer()

if __name__ == "__main__":
    main()