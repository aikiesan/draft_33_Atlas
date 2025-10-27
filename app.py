"""
Atlas 3+3 - Main Application with Interactive Dashboard
A curated atlas of sustainable development projects featuring 30 real-world SDG initiatives

Run with: streamlit run app.py
Updated: 2025-10-27 13:00 - Force fresh deployment to fix st.query_params error
DEPLOYMENT REBUILD: Streamlit Cloud cache invalidation
"""

# Core imports
import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import json
from typing import Dict, List, Any, Optional

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database_interface import get_cached_database
from src.constants import (
    APP_NAME, APP_TAGLINE, APP_VERSION, CONTACT_EMAIL,
    PRIVACY_POLICY_URL, TERMS_OF_SERVICE_URL, UIA_REGIONS, SDGS,
    MAP_MARKER_SETTINGS, DEFAULT_MAP_CENTER, CHART_COLORS
)
from src.utils import (
    is_admin_logged_in, get_session_value, set_session_value,
    format_currency, format_large_number, get_export_filename,
    export_to_csv, export_to_xlsx, get_color_for_status,
    get_color_for_sdg, truncate_text, get_map_bounds
)

# Initialize database using new interface
@st.cache_resource
def get_database():
    return get_cached_database()

def configure_page():
    """Configure the main Streamlit page settings"""
    st.set_page_config(
        page_title=f"{APP_NAME} - Interactive Dashboard",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': f'mailto:{CONTACT_EMAIL}',
            'Report a bug': 'https://github.com/atlas33/issues',
            'About': f"""
            # {APP_NAME}
            {APP_TAGLINE}

            Version: {APP_VERSION}

            A comprehensive platform showcasing innovative sustainable development
            projects from around the world. Our mission is to connect ideas,
            inspire action, and foster collaboration for a more sustainable future.

            ---

            **Contact:** {CONTACT_EMAIL}
            """
        }
    )

def render_sidebar():
    """Render the main navigation sidebar"""
    with st.sidebar:
        # Logo and title
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="color: #0066FF; margin: 0; font-size: 2rem;">🌍 {APP_NAME}</h1>
            <p style="color: #666; margin: 0; font-size: 0.9rem;">{APP_TAGLINE}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Navigation menu
        st.markdown("### 📍 Navigation")

        # Note: Dashboard is now the main page
        st.info("📊 You're viewing the main dashboard")

        # Other pages
        if st.button("🏠 About", use_container_width=True):
            st.switch_page("pages/1_home.py")

        # Submit project
        if st.button("📝 Submit Project", use_container_width=True):
            st.switch_page("pages/3_submit.py")

        # Admin (only if logged in)
        if is_admin_logged_in():
            if st.button("🛠️ Admin Panel", use_container_width=True):
                st.switch_page("pages/4_admin.py")
        else:
            if st.button("🔐 Admin Login", use_container_width=True):
                st.switch_page("pages/4_admin.py")

        st.markdown("---")

        # Quick stats
        render_quick_stats()

        st.markdown("---")

        # Footer
        render_sidebar_footer()

def render_welcome_banner():
    """Render welcome banner for the main dashboard page"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0066FF 0%, #4ECDC4 100%);
        padding: 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        text-align: center;
        color: white;
    ">
        <h1 style="
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        ">🌍 Atlas 3+3 Dashboard</h1>
        <p style="
            font-size: 1.2rem;
            margin: 0;
            opacity: 0.95;
        ">
            Explore 22 verified real-world sustainable development projects from around the globe
        </p>
    </div>
    """, unsafe_allow_html=True)

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
        funding_display = format_currency(funding_needed)
        if funding_needed >= 1000000:
            funding_display = f"${funding_needed/1000000:.1f}M"
        st.metric(
            label="💰 Funding Needed",
            value=funding_display,
            delta=None
        )

    with col5:
        spent_display = format_currency(funding_spent)
        if funding_spent >= 1000000:
            spent_display = f"${funding_spent/1000000:.1f}M"
        st.metric(
            label="✅ Funding Spent",
            value=spent_display,
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
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Filters", use_container_width=True):
            st.session_state.region_filter = "All Regions"
            st.session_state.sdg_filter = "All SDGs"
            st.session_state.city_filter = "All Cities"
            st.session_state.org_filter = "All Organizations"
            st.rerun()

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

    return filters

def render_enhanced_map(projects: List[Dict[str, Any]]):
    """Render enhanced Folium map with bigger display"""
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
        <div style="width: 300px;">
            <h4 style="margin: 0 0 10px 0; color: #0066FF;">{project['project_name']}</h4>
            <p style="margin: 5px 0;"><strong>📍 Location:</strong> {project['city']}, {project['country']}</p>
            <p style="margin: 5px 0;"><strong>📊 Status:</strong> {project['project_status']}</p>
            <p style="margin: 5px 0;"><strong>💰 Funding:</strong> {format_currency(project['funding_needed_usd']) if pd.notna(project['funding_needed_usd']) else 'Not specified'}</p>
            <p style="margin: 5px 0;"><strong>🏢 Organization:</strong> {project['organization_name']}</p>
            <p style="margin: 10px 0 0 0; font-size: 0.9em; color: #666;">{project['brief_description'][:100]}...</p>
        </div>
        """

        folium.Marker(
            location=[project['latitude'], project['longitude']],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=project['project_name'],
            icon=folium.Icon(
                color=marker_settings['color'],
                icon=marker_settings['icon']
            )
        ).add_to(m)

    # Fit map to bounds if available
    if bounds:
        m.fit_bounds(bounds, padding=[20, 20])

    # Display map with enhanced size
    map_data = st_folium(m, width=None, height=800, returned_objects=["last_object_clicked"])

    return map_data

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_quick_stats():
    """Get quick statistics for sidebar"""
    try:
        db = get_cached_database()
        projects = db.get_all_published_projects()

        if not projects:
            return {
                'total_projects': 0,
                'total_countries': 0,
                'total_funding': 0
            }

        import pandas as pd
        df = pd.DataFrame(projects)

        return {
            'total_projects': len(df),
            'total_countries': df['country'].nunique(),
            'total_funding': df['funding_needed_usd'].fillna(0).sum()
        }
    except Exception as e:
        st.error(f"Error loading stats: {e}")
        return {'total_projects': 0, 'total_countries': 0, 'total_funding': 0}

def render_quick_stats():
    """Render quick statistics in sidebar"""
    st.markdown("### 📈 Quick Stats")

    stats = get_quick_stats()

    st.metric("Published Projects", stats['total_projects'])
    st.metric("Countries", stats['total_countries'])

    # Format funding
    funding = stats['total_funding']
    if funding >= 1_000_000:
        funding_display = f"${funding/1_000_000:.1f}M"
    elif funding >= 1_000:
        funding_display = f"${funding/1_000:.1f}K"
    else:
        funding_display = f"${funding:,.0f}"

    st.metric("Total Funding", funding_display)

def render_sidebar_footer():
    """Render sidebar footer with links"""
    st.markdown("### 🔗 Quick Links")

    st.markdown(f"""
    - 📧 [Contact Us](mailto:{CONTACT_EMAIL})
    - 📄 [Privacy Policy]({PRIVACY_POLICY_URL})
    - 📋 [Terms of Service]({TERMS_OF_SERVICE_URL})
    - 💝 [Support Atlas 3+3](https://atlas33.org/donate)
    """)

    # Version info
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; font-size: 0.8rem; color: #666;">
        Version {APP_VERSION}<br>
        © 2025 Atlas 3+3
    </div>
    """, unsafe_allow_html=True)

# Functions removed - dashboard is now the main page

def initialize_database():
    """Initialize the database on first run"""
    try:
        db = get_cached_database()
        # Test database connection
        if db.health_check():
            return True
        else:
            st.error("Database health check failed")
            return False
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        return False

def main():
    """Main application function - Dashboard as landing page"""
    # Configure the page
    configure_page()

    # Initialize database
    if not initialize_database():
        st.stop()

    # Initialize database
    db = get_database()

    # Render sidebar
    render_sidebar()

    # Render welcome banner
    render_welcome_banner()

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

    # Enhanced Map Section - Full Width
    st.subheader("🗺️ Global Project Map")
    st.markdown("*Explore all 22 sustainable development projects across the globe*")

    map_data = render_enhanced_map(filtered_projects)

    st.markdown("---")

    # Quick Analytics Row
    if filtered_projects:
        st.subheader("📊 Quick Analytics")

        col1, col2 = st.columns(2)

        projects_df = pd.DataFrame(filtered_projects)

        with col1:
            # Regional distribution
            region_counts = projects_df.groupby('region_name').size().reset_index(name='count')
            fig_region = px.pie(
                region_counts,
                values='count',
                names='region_name',
                title="Projects by Region"
            )
            fig_region.update_layout(height=400)
            st.plotly_chart(fig_region, use_container_width=True)

        with col2:
            # Status distribution
            status_counts = projects_df.groupby('project_status').size().reset_index(name='count')
            fig_status = px.bar(
                status_counts,
                x='project_status',
                y='count',
                title="Projects by Status",
                color='project_status'
            )
            fig_status.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_status, use_container_width=True)

        st.markdown("---")

        # Projects preview table
        st.subheader("📋 Projects Overview")

        # Simple table view
        display_df = projects_df.copy()
        display_df['funding_display'] = display_df['funding_needed_usd'].apply(
            lambda x: format_currency(x) if pd.notna(x) else "Not specified"
        )

        table_df = display_df[[
            'project_name', 'city', 'country', 'project_status', 'funding_display'
        ]].head(10)  # Show first 10 projects

        table_df.columns = ['Project Name', 'City', 'Country', 'Status', 'Funding Needed']

        st.dataframe(table_df, use_container_width=True, hide_index=True)

        if len(filtered_projects) > 10:
            st.info(f"Showing 10 of {len(filtered_projects)} projects. Use filters above to refine results.")

    else:
        st.info("No projects found matching your current filters.")

    # Footer with navigation hints
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
        <p style="margin: 0;">
            💡 <strong>Tip:</strong> Use the sidebar to navigate to other sections:
            📝 Submit your project | 🏠 Learn more about Atlas 3+3
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    # CACHE_BUST: 2025-10-27-13:00 - Force fresh Streamlit Cloud deployment
    main()