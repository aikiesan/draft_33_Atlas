"""
Atlas 3+3 - Home/Landing Page
A curated atlas of sustainable development projects
"""

import streamlit as st
from src.constants import (
    APP_NAME, APP_TAGLINE, APP_DESCRIPTION, CONTACT_EMAIL, CONTACT_PHONE,
    PRIVACY_POLICY_URL, TERMS_OF_SERVICE_URL, PLACEHOLDER_IMAGES
)

def render_banner():
    """Render hero banner section"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0066FF 0%, #4ECDC4 100%);
        padding: 4rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        text-align: center;
        color: white;
    ">
        <h1 style="
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        ">{}</h1>
        <h2 style="
            font-size: 1.5rem;
            font-weight: 300;
            margin-bottom: 2rem;
            opacity: 0.9;
        ">{}</h2>
        <div style="
            max-width: 800px;
            margin: 0 auto;
            font-size: 1.1rem;
            line-height: 1.6;
            opacity: 0.95;
        ">
            Discover innovative sustainable development projects from around the world.
            Connect with visionary organizations, explore groundbreaking initiatives,
            and contribute to building a more sustainable future for all.
        </div>
    </div>
    """.format(APP_NAME, APP_TAGLINE), unsafe_allow_html=True)

def render_cta_buttons():
    """Render call-to-action buttons"""
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button("🌍 Explore Projects", type="primary", use_container_width=True):
            st.switch_page("app.py")

        if st.button("📝 Submit Your Project", use_container_width=True):
            st.switch_page("pages/3_submit.py")

def render_vision_mission():
    """Render vision and mission section"""
    st.markdown("## 🎯 Our Vision & Mission")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### Vision
        To create a global community where sustainable development projects are easily
        discoverable, replicable, and scalable. We envision a world where innovative
        solutions to environmental and social challenges are shared openly, inspiring
        action and fostering collaboration across borders.

        **Our platform serves as:**
        - A comprehensive atlas of proven sustainable solutions
        - A bridge connecting project innovators with supporters
        - A catalyst for scaling successful initiatives globally
        """)

    with col2:
        st.markdown("""
        ### Mission
        Atlas 3+3 curates and showcases exceptional sustainable development projects
        that align with the UN Sustainable Development Goals. Through our rigorous
        review process, we ensure that featured projects demonstrate real impact,
        innovation, and potential for replication.

        **We focus on projects that:**
        - Address critical sustainability challenges
        - Show measurable positive impact
        - Offer replicable solutions for other communities
        - Foster international collaboration and knowledge sharing
        """)

def render_how_it_works():
    """Render how it works section"""
    st.markdown("## 🔄 How It Works")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 2rem 1rem;
            background: #f8f9fa;
            border-radius: 15px;
            margin-bottom: 1rem;
        ">
            <div style="
                font-size: 3rem;
                color: #0066FF;
                margin-bottom: 1rem;
            ">📝</div>
            <h3 style="color: #0066FF; margin-bottom: 1rem;">1. Submit</h3>
            <p style="margin: 0; line-height: 1.5;">
                Organizations submit their sustainable development projects
                through our comprehensive application form, providing detailed
                information about impact, methodology, and outcomes.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 2rem 1rem;
            background: #f8f9fa;
            border-radius: 15px;
            margin-bottom: 1rem;
        ">
            <div style="
                font-size: 3rem;
                color: #FFC107;
                margin-bottom: 1rem;
            ">🔍</div>
            <h3 style="color: #FFC107; margin-bottom: 1rem;">2. Review</h3>
            <p style="margin: 0; line-height: 1.5;">
                Our expert review panel evaluates submissions based on
                innovation, impact, sustainability, and replicability.
                We ensure only high-quality projects make it to the atlas.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 2rem 1rem;
            background: #f8f9fa;
            border-radius: 15px;
            margin-bottom: 1rem;
        ">
            <div style="
                font-size: 3rem;
                color: #28A745;
                margin-bottom: 1rem;
            ">🌍</div>
            <h3 style="color: #28A745; margin-bottom: 1rem;">3. Share</h3>
            <p style="margin: 0; line-height: 1.5;">
                Approved projects are published in our interactive atlas,
                making them discoverable to a global audience of
                practitioners, funders, and communities seeking solutions.
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_featured_stats():
    """Render featured statistics"""
    st.markdown("## 📊 Global Impact")

    col1, col2, col3, col4 = st.columns(4)

    # These would be dynamic from database in production
    with col1:
        st.metric("Published Projects", "156", "12")

    with col2:
        st.metric("Countries Represented", "42", "3")

    with col3:
        st.metric("Total Funding", "$1.2B", "15%")

    with col4:
        st.metric("SDGs Addressed", "17", "")

def render_call_to_action():
    """Render final call to action section"""
    st.markdown("---")

    st.markdown("""
    <div style="
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #28A745 0%, #20C997 100%);
        border-radius: 20px;
        color: white;
        margin: 2rem 0;
    ">
        <h2 style="margin-bottom: 1rem; font-weight: 600;">Ready to Make an Impact?</h2>
        <p style="
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.95;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        ">
            Join our global community of changemakers. Whether you're showcasing
            your project or seeking inspiration, Atlas 3+3 is your gateway to
            sustainable development solutions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Action buttons
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

    with col2:
        if st.button("🚀 Get Started", type="primary", use_container_width=True):
            st.switch_page("pages/3_submit.py")

    with col4:
        if st.button("📚 Browse Projects", use_container_width=True):
            st.switch_page("app.py")

def render_footer():
    """Render footer section"""
    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(f"""
        ### Contact Information
        - **Email:** {CONTACT_EMAIL}
        - **Phone:** {CONTACT_PHONE}
        - **Website:** [atlas33.org](https://atlas33.org)
        """)

    with col2:
        st.markdown("""
        ### Quick Links
        - [Privacy Policy]({})
        - [Terms of Service]({})
        - [About Us](https://atlas33.org/about)
        """.format(PRIVACY_POLICY_URL, TERMS_OF_SERVICE_URL))

    with col3:
        st.markdown("""
        ### Follow Us
        - [LinkedIn](https://linkedin.com/company/atlas33)
        - [Twitter](https://twitter.com/atlas33org)
        - [Newsletter](https://atlas33.org/newsletter)
        """)

    # Copyright
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #6c757d; font-size: 0.9rem; padding: 1rem 0;'>"
        "© 2025 Atlas 3+3. All rights reserved. | Building a sustainable future, one project at a time."
        "</div>",
        unsafe_allow_html=True
    )

def main():
    """Main function to render the home page"""
    # Page configuration
    st.set_page_config(
        page_title=f"{APP_NAME} - Home",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Remove default padding
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Render page sections
    render_banner()

    # Main content with proper spacing
    col1, col2, col3 = st.columns([1, 10, 1])
    with col2:
        render_cta_buttons()

        st.markdown("<br>", unsafe_allow_html=True)

        render_vision_mission()

        st.markdown("<br>", unsafe_allow_html=True)

        render_how_it_works()

        st.markdown("<br>", unsafe_allow_html=True)

        render_featured_stats()

        render_call_to_action()

        render_footer()

if __name__ == "__main__":
    main()