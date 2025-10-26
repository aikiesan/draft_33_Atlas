"""
Atlas 3+3 - Admin Review Interface
Admin panel for reviewing and managing project submissions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from typing import Dict, List, Any, Optional

from src.database_interface import get_cached_database
from src.constants import (
    APP_NAME, ADMIN_CREDENTIALS, WORKFLOW_STATUSES, SESSION_KEYS,
    ADMIN_QUEUE_PER_PAGE, STATUS_COLORS, SDGS
)
from src.utils import (
    is_admin_logged_in, set_admin_logged_in, clear_session_state,
    get_session_value, set_session_value, create_success_message,
    create_error_message, format_currency, format_date,
    get_color_for_status, paginate_data
)

# Initialize database
@st.cache_resource
def get_database():
    return get_cached_database()

def render_admin_login():
    """Render admin login form"""
    st.title("🔐 Admin Login")
    st.markdown("Please enter your admin credentials to access the review interface.")

    with st.form("admin_login"):
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")

            submitted = st.form_submit_button("🔑 Login", type="primary", use_container_width=True)

            if submitted:
                if (username == ADMIN_CREDENTIALS["username"] and
                    password == ADMIN_CREDENTIALS["password"]):
                    set_admin_logged_in(True)
                    create_success_message("login_success", "Successfully logged in as admin!")
                    st.rerun()
                else:
                    create_error_message("invalid_credentials", "Invalid username or password.")

    # Demo credentials info
    with st.expander("🔍 Demo Credentials", expanded=False):
        st.info(f"""
        **For demonstration purposes:**
        - Username: `{ADMIN_CREDENTIALS['username']}`
        - Password: `{ADMIN_CREDENTIALS['password']}`

        *Note: In production, this would use proper authentication.*
        """)

def render_admin_header():
    """Render admin interface header with logout"""
    col1, col2 = st.columns([4, 1])

    with col1:
        st.title("🛠️ Admin Review Interface")
        st.markdown("Manage project submissions and review queue")

    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            clear_session_state()
            st.rerun()

def render_admin_navigation():
    """Render admin navigation tabs"""
    return st.radio(
        "Navigation",
        options=["📋 Review Queue", "📊 Admin Metrics", "🔍 Project Search"],
        horizontal=True,
        key="admin_nav"
    )

def render_review_queue():
    """Render pending submissions queue"""
    st.subheader("📋 Pending Review Queue")

    db = get_database()
    pending_projects = db.get_pending_reviews()

    if not pending_projects:
        st.info("🎉 No projects pending review! All caught up.")
        return

    # Queue statistics
    col1, col2, col3, col4 = st.columns(4)

    status_counts = {}
    for project in pending_projects:
        status = project['workflow_status']
        status_counts[status] = status_counts.get(status, 0) + 1

    with col1:
        st.metric("Total Pending", len(pending_projects))

    with col2:
        st.metric("New Submissions", status_counts.get('submitted', 0))

    with col3:
        st.metric("In Review", status_counts.get('in_review', 0))

    with col4:
        st.metric("Changes Requested", status_counts.get('changes_requested', 0))

    st.markdown("---")

    # Filter and search
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All"] + [status for status in WORKFLOW_STATUSES if status != 'approved'],
            key="status_filter"
        )

    with col2:
        search_term = st.text_input("🔍 Search projects", placeholder="Project name or organization...")

    with col3:
        sort_by = st.selectbox("Sort by", ["created_at", "project_name", "workflow_status"])

    # Apply filters
    filtered_projects = pending_projects.copy()

    if status_filter != "All":
        filtered_projects = [p for p in filtered_projects if p['workflow_status'] == status_filter]

    if search_term:
        filtered_projects = [
            p for p in filtered_projects
            if (search_term.lower() in p['project_name'].lower() or
                search_term.lower() in p['organization_name'].lower())
        ]

    # Sort projects
    reverse = sort_by == "created_at"  # Most recent first for created_at
    filtered_projects.sort(
        key=lambda x: x.get(sort_by, ''),
        reverse=reverse
    )

    # Pagination
    page = st.selectbox(
        "Page",
        range(1, max(1, len(filtered_projects) // ADMIN_QUEUE_PER_PAGE + 1) + 1),
        format_func=lambda x: f"Page {x}"
    )

    page_projects, total_pages = paginate_data(filtered_projects, page, ADMIN_QUEUE_PER_PAGE)

    # Display projects table
    if page_projects:
        st.markdown(f"Showing {len(page_projects)} of {len(filtered_projects)} projects")

        # Create table data
        table_data = []
        for project in page_projects:
            table_data.append({
                "Project Name": project['project_name'],
                "Organization": project['organization_name'],
                "Location": f"{project['city']}, {project['country']}",
                "Status": project['workflow_status'],
                "Submitted": format_date(project['created_at']),
                "Funding": format_currency(project['funding_needed_usd']) if project['funding_needed_usd'] else "Not specified"
            })

        df = pd.DataFrame(table_data)

        # Display with selection
        event = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        # Handle selection
        if event.selection.rows:
            selected_idx = event.selection.rows[0]
            selected_project = page_projects[selected_idx]
            set_session_value("selected_project_for_review", selected_project['id'])
            set_session_value("show_review_detail", True)

    else:
        st.info("No projects match your current filters.")

def render_project_review_detail():
    """Render detailed project review interface"""
    project_id = get_session_value("selected_project_for_review")

    if not project_id:
        return

    db = get_database()
    project = db.get_project_by_id(project_id)

    if not project:
        create_error_message("project_not_found")
        return

    # Header with close button
    col1, col2 = st.columns([10, 1])
    with col1:
        st.subheader(f"📄 Review: {project['project_name']}")
    with col2:
        if st.button("✖️", help="Close Review", key="close_review"):
            set_session_value("show_review_detail", False)
            st.rerun()

    # Project status info
    status_color = get_color_for_status(project['workflow_status'])
    st.markdown(f"""
    **Current Status:** <span style="background-color: {status_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">{project['workflow_status']}</span>
    """, unsafe_allow_html=True)

    # Project information in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Basic Info", "🎯 SDGs & Requirements", "📸 Media", "⚖️ Review Actions"])

    with tab1:
        # Basic project information
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Project Details")
            st.markdown(f"**Name:** {project['project_name']}")
            st.markdown(f"**Organization:** {project['organization_name']}")
            st.markdown(f"**Contact:** {project['contact_person']} ({project['contact_email']})")
            st.markdown(f"**Location:** {project['city']}, {project['country']}")
            st.markdown(f"**Region:** {project['region_name']}")
            st.markdown(f"**Status:** {project['project_status']}")

            if project['funding_needed_usd']:
                st.markdown(f"**Funding Needed:** {format_currency(project['funding_needed_usd'])}")

            if project['latitude'] and project['longitude']:
                st.markdown(f"**Coordinates:** {project['latitude']}, {project['longitude']}")

        with col2:
            st.markdown("### Descriptions")
            st.markdown("**Brief Description:**")
            st.write(project['brief_description'])

            st.markdown("**Detailed Description:**")
            with st.expander("View full description"):
                st.write(project['detailed_description'])

            if project.get('success_factors'):
                st.markdown("**Success Factors:**")
                with st.expander("View success factors"):
                    st.write(project['success_factors'])

    with tab2:
        # SDGs and Requirements
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Selected SDGs")
            if project.get('sdgs'):
                sdg_html = ""
                for sdg in project['sdgs']:
                    color = sdg['color']
                    sdg_html += f'<span style="background-color: {color}; color: white; padding: 4px 8px; border-radius: 4px; margin: 2px; display: inline-block; font-size: 0.8em;">{sdg["id"]}. {sdg["name"]}</span><br>'
                st.markdown(sdg_html, unsafe_allow_html=True)
            else:
                st.info("No SDGs selected")

        with col2:
            st.markdown("### Project Requirements")
            if project.get('requirements'):
                requirements_by_category = {}
                for req in project['requirements']:
                    category = req['requirement_category']
                    if category not in requirements_by_category:
                        requirements_by_category[category] = []
                    requirements_by_category[category].append(req['requirement_text'])

                for category, reqs in requirements_by_category.items():
                    st.markdown(f"**{category}:**")
                    for req in reqs:
                        st.markdown(f"- {req}")
            else:
                st.info("No requirements specified")

            # Typologies
            st.markdown("### Project Typologies")
            if project.get('typologies'):
                for typology in project['typologies']:
                    st.markdown(f"- {typology['typology']}")
            else:
                st.info("No typologies specified")

    with tab3:
        # Media and images
        st.markdown("### Project Images")
        if project.get('images'):
            for i, img in enumerate(project['images']):
                if img['image_url']:
                    try:
                        st.image(img['image_url'], caption=f"Image {i+1}: {img.get('alt_text', '')}", use_column_width=True)
                    except:
                        st.error(f"Could not load image {i+1}: {img['image_url']}")
        else:
            st.info("No images provided")

    with tab4:
        # Review actions
        render_review_actions(project)

def render_review_actions(project: Dict[str, Any]):
    """Render review action controls"""
    st.markdown("### Review Actions")

    # Review form
    with st.form("review_form"):
        action = st.radio(
            "Select Action",
            options=["Approve & Publish", "Reject", "Request Changes"],
            help="Choose the appropriate action for this project"
        )

        notes = st.text_area(
            "Review Notes",
            placeholder="Add notes about your decision (required for reject/request changes)",
            help="Provide feedback to the submitter"
        )

        # Review checklist
        st.markdown("**Review Checklist:**")
        content_accurate = st.checkbox("Content is accurate and well-written")
        images_appropriate = st.checkbox("Images are appropriate and relevant")
        no_spam = st.checkbox("Project is legitimate (not spam)")

        submitted = st.form_submit_button("🚀 Submit Review", type="primary")

        if submitted:
            handle_review_action(project, action, notes, {
                'content_accurate': content_accurate,
                'images_appropriate': images_appropriate,
                'no_spam': no_spam
            })

def handle_review_action(project: Dict[str, Any], action: str, notes: str, checklist: Dict[str, bool]):
    """Handle review action submission"""
    if action in ["Reject", "Request Changes"] and not notes.strip():
        create_error_message("review_notes_required", "Please provide notes for reject/request changes actions.")
        return

    try:
        db = get_database()

        # Map action to status
        status_map = {
            "Approve & Publish": "approved",
            "Reject": "rejected",
            "Request Changes": "changes_requested"
        }

        new_status = status_map[action]

        # Update project status
        db.update_project_status(
            project_id=project['id'],
            new_status=new_status,
            reason=notes,
            reviewer_id=1  # Admin user ID (would be dynamic in production)
        )

        # Success message
        action_messages = {
            "approved": f"Project '{project['project_name']}' has been approved and published!",
            "rejected": f"Project '{project['project_name']}' has been rejected.",
            "changes_requested": f"Changes have been requested for project '{project['project_name']}'."
        }

        create_success_message("review_complete", action_messages[new_status])

        # Clear selection
        set_session_value("show_review_detail", False)
        set_session_value("selected_project_for_review", None)

        st.rerun()

    except Exception as e:
        create_error_message("review_error", f"Error processing review: {str(e)}")

def render_admin_metrics():
    """Render admin metrics dashboard"""
    st.subheader("📊 Admin Metrics Dashboard")

    db = get_database()
    metrics = db.get_admin_metrics()

    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Pending Reviews", metrics['pending_reviews'])

    with col2:
        st.metric("Approved (This Month)", metrics['approved_this_month'])

    with col3:
        st.metric("Rejected (This Month)", metrics['rejected_this_month'])

    with col4:
        st.metric("Total Published", metrics['total_published'])

    with col5:
        st.metric("Avg Review Time", metrics['avg_review_time'])

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        # Workflow status distribution
        all_projects = db.get_all_published_projects()
        pending_projects = db.get_pending_reviews()

        status_data = {}
        for project in all_projects:
            status = project.get('workflow_status', 'unknown')
            status_data[status] = status_data.get(status, 0) + 1

        for project in pending_projects:
            status = project.get('workflow_status', 'unknown')
            status_data[status] = status_data.get(status, 0) + 1

        if status_data:
            fig = px.pie(
                values=list(status_data.values()),
                names=list(status_data.keys()),
                title="Project Status Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Monthly submission trend (placeholder)
        import datetime
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        submissions = [12, 15, 18, 14, 20, 16]

        fig = px.line(
            x=months,
            y=submissions,
            title="Monthly Submissions Trend",
            markers=True
        )
        fig.update_xaxis(title="Month")
        fig.update_yaxis(title="Number of Submissions")
        st.plotly_chart(fig, use_container_width=True)

def render_project_search():
    """Render admin project search interface"""
    st.subheader("🔍 Project Search & Management")

    db = get_database()

    # Search controls
    col1, col2, col3 = st.columns(3)

    with col1:
        search_term = st.text_input("Search Projects", placeholder="Project name, organization, or email...")

    with col2:
        status_filter = st.selectbox("Status Filter", options=["All"] + WORKFLOW_STATUSES)

    with col3:
        region_filter = st.selectbox("Region Filter", options=["All"] + list(db.get_database().execute("SELECT DISTINCT region_name FROM projects p JOIN uia_regions ur ON p.uia_region_id = ur.id").fetchall()))

    # Get all projects (including non-published for admin)
    all_projects = db.get_all_published_projects() + db.get_pending_reviews()

    # Apply filters
    filtered_projects = all_projects

    if search_term:
        filtered_projects = [
            p for p in filtered_projects
            if (search_term.lower() in p['project_name'].lower() or
                search_term.lower() in p['organization_name'].lower() or
                search_term.lower() in p.get('contact_email', '').lower())
        ]

    if status_filter != "All":
        filtered_projects = [p for p in filtered_projects if p['workflow_status'] == status_filter]

    # Display results
    st.markdown(f"Found {len(filtered_projects)} projects")

    if filtered_projects:
        # Create simplified table
        table_data = []
        for project in filtered_projects:
            table_data.append({
                "ID": project['id'],
                "Project Name": project['project_name'],
                "Organization": project['organization_name'],
                "Status": project['workflow_status'],
                "Created": format_date(project['created_at']),
            })

        df = pd.DataFrame(table_data)

        # Display with selection
        event = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        # Handle selection for quick actions
        if event.selection.rows:
            selected_idx = event.selection.rows[0]
            selected_project = filtered_projects[selected_idx]

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("📄 View Details"):
                    set_session_value("selected_project_for_review", selected_project['id'])
                    set_session_value("show_review_detail", True)

            with col2:
                if selected_project['workflow_status'] != 'approved':
                    if st.button("✅ Quick Approve"):
                        db.update_project_status(selected_project['id'], 'approved', 'Quick approval via admin search')
                        st.success("Project approved!")
                        st.rerun()

            with col3:
                if selected_project['workflow_status'] == 'approved':
                    if st.button("📴 Unpublish"):
                        db.update_project_status(selected_project['id'], 'in_review', 'Unpublished via admin panel')
                        st.warning("Project unpublished!")
                        st.rerun()

            with col4:
                if st.button("🗑️ Delete", type="secondary"):
                    st.error("Delete functionality would be implemented here (with confirmation)")

def main():
    """Main admin interface function"""
    # Page configuration
    st.set_page_config(
        page_title=f"{APP_NAME} - Admin",
        page_icon="🛠️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Check admin authentication
    if not is_admin_logged_in():
        render_admin_login()
        return

    # Render admin interface
    render_admin_header()

    # Navigation
    current_tab = render_admin_navigation()

    st.markdown("---")

    # Show review detail if selected
    if get_session_value("show_review_detail", False):
        render_project_review_detail()
        st.markdown("---")

    # Render content based on navigation
    if current_tab == "📋 Review Queue":
        render_review_queue()
    elif current_tab == "📊 Admin Metrics":
        render_admin_metrics()
    elif current_tab == "🔍 Project Search":
        render_project_search()

if __name__ == "__main__":
    main()