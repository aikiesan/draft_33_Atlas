"""
Atlas 3+3 - Main Application Entry Point
A curated atlas of sustainable development projects

Run with: streamlit run app.py
"""

import streamlit as st
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database_interface import get_cached_database
from src.constants import (
    APP_NAME, APP_TAGLINE, APP_VERSION, CONTACT_EMAIL,
    PRIVACY_POLICY_URL, TERMS_OF_SERVICE_URL
)
from src.utils import is_admin_logged_in, get_session_value

def configure_page():
    """Configure the main Streamlit page settings"""
    st.set_page_config(
        page_title=APP_NAME,
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

        # Home page
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("pages/1_home.py")

        # Dashboard
        if st.button("📊 Dashboard", use_container_width=True):
            st.switch_page("pages/2_dashboard.py")

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

def render_main_content():
    """Render the main content area (home page by default)"""
    # Check if we should redirect to a specific page
    query_params = st.query_params

    if "page" in query_params:
        page = query_params["page"]
        if page == "dashboard":
            st.switch_page("pages/2_dashboard.py")
        elif page == "submit":
            st.switch_page("pages/3_submit.py")
        elif page == "admin":
            st.switch_page("pages/4_admin.py")

    # Default to home page content
    render_home_page()

def render_home_page():
    """Render the home page content in main area"""
    # Welcome banner
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0066FF 0%, #4ECDC4 100%);
        padding: 3rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        text-align: center;
        color: white;
    ">
        <h1 style="
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        ">Welcome to Atlas 3+3</h1>
        <h2 style="
            font-size: 1.3rem;
            font-weight: 300;
            margin-bottom: 1.5rem;
            opacity: 0.9;
        ">Discover, Share, and Scale Sustainable Development Projects</h2>
        <p style="
            max-width: 700px;
            margin: 0 auto;
            font-size: 1.1rem;
            line-height: 1.6;
            opacity: 0.95;
        ">
            Explore innovative projects from around the world that are making a real difference
            in communities. Connect with changemakers, find inspiration, and contribute to
            building a more sustainable future.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Main action buttons
    st.markdown("### 🚀 Get Started")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🌍 Explore Projects", type="primary", use_container_width=True, help="Browse our curated collection of sustainable development projects"):
            st.switch_page("pages/2_dashboard.py")

        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; margin-top: 1rem;">
            <h4>🔍 Discover</h4>
            <p style="margin: 0; font-size: 0.9rem;">Browse interactive maps, charts, and detailed project information from around the globe.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("📝 Submit Your Project", use_container_width=True, help="Share your sustainable development project with the global community"):
            st.switch_page("pages/3_submit.py")

        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; margin-top: 1rem;">
            <h4>📤 Share</h4>
            <p style="margin: 0; font-size: 0.9rem;">Submit your project for review and publication in our global atlas.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        if st.button("💡 Learn More", use_container_width=True, help="Learn about our mission and how Atlas 3+3 works"):
            st.switch_page("pages/1_home.py")

        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; margin-top: 1rem;">
            <h4>🎯 Connect</h4>
            <p style="margin: 0; font-size: 0.9rem;">Learn about our mission and connect with other changemakers worldwide.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Featured highlights
    st.markdown("### 🌟 Platform Highlights")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### 🗺️ Interactive Global Map
        Explore projects on an interactive world map with detailed location data,
        project status indicators, and easy filtering by region, SDG, or project type.

        #### 📊 Rich Analytics
        Dive deep into project data with comprehensive charts showing SDG distribution,
        funding patterns, regional analysis, and implementation progress.
        """)

    with col2:
        st.markdown("""
        #### 🎯 SDG Alignment
        All projects are mapped to the UN Sustainable Development Goals, making it
        easy to find initiatives that align with specific global priorities.

        #### 🔍 Rigorous Review
        Our expert review panel ensures that only high-quality, impactful projects
        with replication potential are featured in the atlas.
        """)

    # Recent activity or featured content could go here
    st.markdown("---")

    # Call to action
    st.markdown("""
    <div style="
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #28A745 0%, #20C997 100%);
        border-radius: 15px;
        color: white;
        margin: 2rem 0;
    ">
        <h3 style="margin-bottom: 1rem;">Ready to Make an Impact?</h3>
        <p style="margin-bottom: 1.5rem; opacity: 0.9;">
            Join our global community of sustainable development practitioners,
            researchers, and changemakers.
        </p>
    </div>
    """, unsafe_allow_html=True)

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
    """Main application function"""
    # Configure the page
    configure_page()

    # Initialize database
    if not initialize_database():
        st.stop()

    # Render sidebar
    render_sidebar()

    # Render main content
    render_main_content()

if __name__ == "__main__":
    main()