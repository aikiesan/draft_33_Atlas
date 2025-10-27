"""
Atlas 3+3 - Project Submission Form
Multi-section form for submitting new projects
"""

import streamlit as st
import re
from typing import Dict, List, Any, Optional

from src.database_interface import get_cached_database
from src.constants import (
    APP_NAME, UIA_REGIONS, SDGS, PROJECT_TYPOLOGIES, PROJECT_REQUIREMENTS,
    PROJECT_STATUSES, MAX_BRIEF_DESCRIPTION_LENGTH, MAX_DETAILED_DESCRIPTION_LENGTH,
    MAX_SUCCESS_FACTORS_LENGTH, SUCCESS_MESSAGES, SESSION_KEYS
)
from src.utils import (
    validate_project_form, validate_email, validate_url, validate_coordinates,
    parse_coordinates, clean_string, generate_reference_id,
    create_success_message, create_error_message, get_session_value, set_session_value
)

# Initialize database
@st.cache_resource
def get_database():
    return get_cached_database()

def initialize_form_data():
    """Initialize empty form data in session state"""
    if "form_data" not in st.session_state:
        st.session_state.form_data = {
            # Section 1: Project Status
            "project_status": "",

            # Section 2: Submitter Information
            "organization_name": "",
            "contact_person": "",
            "contact_email": "",

            # Section 3: Project Details
            "project_name": "",
            "funding_needed_usd": None,
            "uia_region_id": None,
            "city": "",
            "country": "",
            "latitude": None,
            "longitude": "",

            # Section 4: Project Typology
            "typologies": [],
            "other_typology": "",

            # Section 5: Project Media & Description
            "image_urls": [""],
            "brief_description": "",
            "detailed_description": "",

            # Section 6: Key Requirements & SDGs
            "requirements": [],
            "other_requirement": "",
            "success_factors": "",
            "sdgs": []
        }

def render_section_1():
    """Section 1: Project Status"""
    st.subheader("📊 Section 1: Project Status")

    project_status = st.selectbox(
        "Project Status *",
        options=[""] + PROJECT_STATUSES,
        index=0 if not st.session_state.form_data["project_status"] else PROJECT_STATUSES.index(st.session_state.form_data["project_status"]) + 1,
        help="Select the current implementation status of your project"
    )

    st.session_state.form_data["project_status"] = project_status

def render_section_2():
    """Section 2: Submitter Information"""
    st.subheader("👤 Section 2: Submitter Information")

    col1, col2 = st.columns(2)

    with col1:
        organization_name = st.text_input(
            "Organization/Municipality/University Name *",
            value=st.session_state.form_data["organization_name"],
            help="The name of your organization"
        )
        st.session_state.form_data["organization_name"] = clean_string(organization_name)

        contact_person = st.text_input(
            "Contact Person *",
            value=st.session_state.form_data["contact_person"],
            help="Primary contact person for this project"
        )
        st.session_state.form_data["contact_person"] = clean_string(contact_person)

    with col2:
        contact_email = st.text_input(
            "Contact Email *",
            value=st.session_state.form_data["contact_email"],
            help="Email address for project communications"
        )
        st.session_state.form_data["contact_email"] = clean_string(contact_email)

        # Email validation feedback
        if contact_email and not validate_email(contact_email):
            st.error("Please enter a valid email address")

def render_section_3():
    """Section 3: Project Details"""
    st.subheader("📍 Section 3: Project Details")

    # Project name and funding
    col1, col2 = st.columns(2)

    with col1:
        project_name = st.text_input(
            "Project Name *",
            value=st.session_state.form_data["project_name"],
            help="The official name of your project"
        )
        st.session_state.form_data["project_name"] = clean_string(project_name)

        funding_needed = st.number_input(
            "Funding Needed (USD)",
            min_value=0.0,
            value=st.session_state.form_data["funding_needed_usd"] or 0.0,
            help="Total funding required for project implementation"
        )
        st.session_state.form_data["funding_needed_usd"] = funding_needed if funding_needed > 0 else None

    with col2:
        uia_region = st.selectbox(
            "UIA Region *",
            options=[""] + list(UIA_REGIONS.values()),
            index=0 if not st.session_state.form_data["uia_region_id"] else list(UIA_REGIONS.values()).index(
                list(UIA_REGIONS.values())[st.session_state.form_data["uia_region_id"] - 1]
            ) + 1 if st.session_state.form_data["uia_region_id"] else 0,
            help="Select the UIA region where your project is located"
        )

        if uia_region:
            for region_id, region_name in UIA_REGIONS.items():
                if region_name == uia_region:
                    st.session_state.form_data["uia_region_id"] = region_id
                    break
        else:
            st.session_state.form_data["uia_region_id"] = None

    # Location details
    col1, col2 = st.columns(2)

    with col1:
        city = st.text_input(
            "City *",
            value=st.session_state.form_data["city"],
            help="The city where your project is located"
        )
        st.session_state.form_data["city"] = clean_string(city)

        country = st.text_input(
            "Country *",
            value=st.session_state.form_data["country"],
            help="The country where your project is located"
        )
        st.session_state.form_data["country"] = clean_string(country)

    with col2:
        latitude = st.number_input(
            "Latitude (optional)",
            min_value=-90.0,
            max_value=90.0,
            value=st.session_state.form_data["latitude"] or 0.0,
            format="%.6f",
            help="Latitude coordinate (between -90 and 90)"
        )

        longitude = st.text_input(
            "Longitude (optional)",
            value=str(st.session_state.form_data["longitude"]) if st.session_state.form_data["longitude"] else "",
            help="Longitude coordinate (between -180 and 180)"
        )

        # Handle coordinate validation
        lat, lon = parse_coordinates(str(latitude), longitude)
        is_valid, error_msg = validate_coordinates(lat, lon)

        if not is_valid and error_msg:
            st.error(error_msg)
        else:
            st.session_state.form_data["latitude"] = lat
            st.session_state.form_data["longitude"] = lon

def render_section_4():
    """Section 4: Project Typology"""
    st.subheader("🏗️ Section 4: Project Typology")

    st.markdown("Select all typologies that apply to your project:")

    # Create checkboxes for typologies
    selected_typologies = []

    # Display typologies in columns
    cols = st.columns(3)

    for i, typology in enumerate(PROJECT_TYPOLOGIES):
        col_idx = i % 3
        with cols[col_idx]:
            if typology == "Other":
                is_selected = st.checkbox(
                    typology,
                    value=typology in st.session_state.form_data["typologies"],
                    key=f"typology_{typology}"
                )
                if is_selected:
                    other_desc = st.text_input(
                        "Describe other typology:",
                        value=st.session_state.form_data["other_typology"],
                        key="other_typology_desc"
                    )
                    st.session_state.form_data["other_typology"] = clean_string(other_desc)
                    if other_desc.strip():
                        selected_typologies.append(f"Other: {other_desc.strip()}")
            else:
                is_selected = st.checkbox(
                    typology,
                    value=typology in st.session_state.form_data["typologies"],
                    key=f"typology_{typology}"
                )
                if is_selected:
                    selected_typologies.append(typology)

    st.session_state.form_data["typologies"] = selected_typologies

def render_section_5():
    """Section 5: Project Media & Description"""
    st.subheader("📸 Section 5: Project Media & Description")

    # Image URLs
    st.markdown("**Project Image URLs:**")
    st.markdown("Add URLs to images that showcase your project (optional)")

    # Initialize image URLs if empty
    if not st.session_state.form_data["image_urls"]:
        st.session_state.form_data["image_urls"] = [""]

    # Dynamic image URL inputs
    for i in range(len(st.session_state.form_data["image_urls"])):
        col1, col2 = st.columns([4, 1])

        with col1:
            url = st.text_input(
                f"Image URL {i+1}",
                value=st.session_state.form_data["image_urls"][i],
                key=f"image_url_{i}",
                help="Enter a valid URL starting with http:// or https://"
            )
            st.session_state.form_data["image_urls"][i] = clean_string(url)

            # URL validation
            if url and not validate_url(url):
                st.error(f"Invalid URL format for image {i+1}")
            elif url:
                try:
                    st.image(url, caption=f"Image {i+1} Preview", width=200)
                except:
                    st.warning(f"Could not load image preview for URL {i+1}")

        with col2:
            if i == len(st.session_state.form_data["image_urls"]) - 1:
                if st.button("➕", key=f"add_image_{i}", help="Add another image"):
                    st.session_state.form_data["image_urls"].append("")
                    st.rerun()
            else:
                if st.button("🗑️", key=f"remove_image_{i}", help="Remove this image"):
                    st.session_state.form_data["image_urls"].pop(i)
                    st.rerun()

    # Descriptions
    st.markdown("**Project Descriptions:**")

    brief_description = st.text_area(
        f"Brief Description * (max {MAX_BRIEF_DESCRIPTION_LENGTH} characters)",
        value=st.session_state.form_data["brief_description"],
        max_chars=MAX_BRIEF_DESCRIPTION_LENGTH,
        help="A short summary of your project (1-2 sentences)"
    )
    st.session_state.form_data["brief_description"] = clean_string(brief_description)

    # Character counter
    brief_char_count = len(brief_description)
    st.caption(f"{brief_char_count}/{MAX_BRIEF_DESCRIPTION_LENGTH} characters")

    detailed_description = st.text_area(
        f"Detailed Description * (max {MAX_DETAILED_DESCRIPTION_LENGTH} characters)",
        value=st.session_state.form_data["detailed_description"],
        max_chars=MAX_DETAILED_DESCRIPTION_LENGTH,
        height=150,
        help="Comprehensive description of your project, including methodology, impact, and outcomes"
    )
    st.session_state.form_data["detailed_description"] = clean_string(detailed_description)

    # Character counter
    detailed_char_count = len(detailed_description)
    st.caption(f"{detailed_char_count}/{MAX_DETAILED_DESCRIPTION_LENGTH} characters")

def render_section_6():
    """Section 6: Key Requirements & SDGs"""
    st.subheader("✅ Section 6: Key Requirements & SDGs")

    # Sub-section 6a: Key Requirements
    st.markdown("**6a. Key Requirements for Realization**")
    st.markdown("Select all requirements that apply to your project:")

    selected_requirements = []

    for category, requirements in PROJECT_REQUIREMENTS.items():
        st.markdown(f"*{category}:*")

        for requirement in requirements:
            if requirement == "Other":
                is_selected = st.checkbox(
                    requirement,
                    value=f"{category}: {requirement}" in st.session_state.form_data["requirements"],
                    key=f"req_{category}_{requirement}"
                )
                if is_selected:
                    other_desc = st.text_input(
                        "Describe other requirement:",
                        value=st.session_state.form_data["other_requirement"],
                        key=f"other_req_{category}"
                    )
                    st.session_state.form_data["other_requirement"] = clean_string(other_desc)
                    if other_desc.strip():
                        selected_requirements.append(f"{category}: Other - {other_desc.strip()}")
            else:
                is_selected = st.checkbox(
                    requirement,
                    value=f"{category}: {requirement}" in st.session_state.form_data["requirements"],
                    key=f"req_{category}_{requirement}"
                )
                if is_selected:
                    selected_requirements.append(f"{category}: {requirement}")

    st.session_state.form_data["requirements"] = selected_requirements

    # Sub-section 6b: Success Factors
    st.markdown("**6b. Success Factors**")

    success_factors = st.text_area(
        f"Why is the project (potentially) successful/needed? * (max {MAX_SUCCESS_FACTORS_LENGTH} characters)",
        value=st.session_state.form_data["success_factors"],
        max_chars=MAX_SUCCESS_FACTORS_LENGTH,
        height=100,
        help="Explain what makes your project successful or why it's needed"
    )
    st.session_state.form_data["success_factors"] = clean_string(success_factors)

    # Character counter
    success_char_count = len(success_factors)
    st.caption(f"{success_char_count}/{MAX_SUCCESS_FACTORS_LENGTH} characters")

    # Sub-section 6c: Select SDGs
    st.markdown("**6c. Select Sustainable Development Goals (SDGs)**")
    st.markdown("Select all SDGs that your project addresses:")

    selected_sdgs = []

    # Display SDGs in a grid
    cols = st.columns(3)

    for i, (sdg_id, sdg_info) in enumerate(SDGS.items()):
        col_idx = i % 3
        with cols[col_idx]:
            is_selected = st.checkbox(
                f"{sdg_id}. {sdg_info['name']}",
                value=sdg_id in st.session_state.form_data["sdgs"],
                key=f"sdg_{sdg_id}"
            )
            if is_selected:
                selected_sdgs.append(sdg_id)

    st.session_state.form_data["sdgs"] = selected_sdgs

    # Show selected SDGs with colors
    if selected_sdgs:
        st.markdown("**Selected SDGs:**")
        sdg_html = ""
        for sdg_id in selected_sdgs:
            sdg_info = SDGS[sdg_id]
            color = sdg_info['color']
            sdg_html += f'<span style="background-color: {color}; color: white; padding: 4px 8px; border-radius: 4px; margin: 2px; display: inline-block; font-size: 0.8em;">{sdg_id}. {sdg_info["name"]}</span> '
        st.markdown(sdg_html, unsafe_allow_html=True)

def render_form_actions():
    """Section 7: Form Actions"""
    st.subheader("🚀 Submit Your Project")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📤 Submit Project", type="primary", use_container_width=True):
            handle_form_submission()

    with col2:
        if st.button("🗑️ Clear Form", use_container_width=True):
            if st.session_state.get("confirm_clear", False):
                # Clear the form
                initialize_form_data()
                st.session_state.confirm_clear = False
                create_success_message("form_cleared", "Form has been cleared successfully!")
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("Click again to confirm clearing the form")

    with col3:
        if st.button("💾 Save Draft", use_container_width=True):
            st.info("Draft saving feature will be available in a future update")

def handle_form_submission():
    """Handle form submission with validation"""
    # Validate form data
    errors = validate_project_form(st.session_state.form_data)

    if errors:
        st.error("Please fix the following errors:")
        for error in errors:
            st.error(f"• {error}")
        return

    try:
        # Prepare data for database
        form_data = st.session_state.form_data.copy()

        # Clean up image URLs (remove empty ones)
        form_data["image_urls"] = [url for url in form_data["image_urls"] if url.strip()]

        # Convert requirements to proper format
        requirements_list = []
        for req_string in form_data["requirements"]:
            if ": " in req_string:
                category, text = req_string.split(": ", 1)
                requirements_list.append({"category": category, "text": text})
        form_data["requirements"] = requirements_list

        # Submit to database
        db = get_database()
        reference_id = db.create_project(form_data)

        # Show confirmation
        render_confirmation_screen(reference_id)

    except Exception as e:
        st.error(f"An error occurred while submitting your project: {str(e)}")
        st.error("Please try again or contact support if the problem persists.")

def render_confirmation_screen(reference_id: str):
    """Render submission confirmation screen"""
    st.success("🎉 Project Submitted Successfully!")

    # Clear the form data
    if "form_data" in st.session_state:
        del st.session_state["form_data"]

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(f"""
        <div style="
            text-align: center;
            padding: 2rem;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #28a745;
        ">
            <h3 style="color: #28a745;">✅ Submission Confirmed</h3>
            <p><strong>Reference ID:</strong> <code>{reference_id}</code></p>
            <hr>
            <p>Your project has been submitted for review by our expert panel.</p>
            <p>You will receive an email at <strong>{st.session_state.form_data.get('contact_email', 'your email')}</strong> when the review is complete.</p>
            <p><em>Review typically takes 3-5 business days.</em></p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col1_inner, col2_inner = st.columns(2)

        with col1_inner:
            if st.button("🏠 Back to Dashboard", use_container_width=True):
                st.switch_page("app.py")

        with col2_inner:
            if st.button("➕ Submit Another Project", use_container_width=True):
                initialize_form_data()
                st.rerun()

def main():
    """Main submission form function"""
    # Page configuration
    st.set_page_config(
        page_title=f"{APP_NAME} - Submit Project",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("📝 Submit Your Project")
    st.markdown("Share your sustainable development project with the global community")

    # Initialize form data
    initialize_form_data()

    # Check if we're showing confirmation screen
    if get_session_value("show_confirmation", False):
        reference_id = get_session_value("reference_id", "")
        render_confirmation_screen(reference_id)
        return

    # Progress indicator
    st.markdown("### 📋 Project Submission Form")
    st.markdown("Please complete all sections below. Fields marked with * are required.")

    # Create form sections
    with st.form("project_submission", clear_on_submit=False):
        # Render all sections
        render_section_1()
        st.markdown("---")

        render_section_2()
        st.markdown("---")

        render_section_3()
        st.markdown("---")

        render_section_4()
        st.markdown("---")

        render_section_5()
        st.markdown("---")

        render_section_6()
        st.markdown("---")

        # Form submission
        submitted = st.form_submit_button("📤 Submit Project", type="primary", use_container_width=True)

        if submitted:
            handle_form_submission()

    # Additional actions outside form
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ Clear Form"):
            initialize_form_data()
            st.success("Form cleared successfully!")
            st.rerun()

    with col2:
        if st.button("🏠 Back to Home"):
            st.switch_page("pages/1_home.py")

if __name__ == "__main__":
    main()