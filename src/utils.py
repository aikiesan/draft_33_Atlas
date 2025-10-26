"""
Utility functions for Atlas 3+3 application
"""

import re
import io
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import streamlit as st
from src.constants import (
    EMAIL_REGEX, URL_REGEX, CURRENCY_SYMBOL, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX,
    MAX_PROJECT_NAME_LENGTH, MAX_BRIEF_DESCRIPTION_LENGTH, MAX_DETAILED_DESCRIPTION_LENGTH,
    MAX_SUCCESS_FACTORS_LENGTH, MAX_ORGANIZATION_NAME_LENGTH, MAX_CONTACT_PERSON_LENGTH,
    MIN_FUNDING_AMOUNT, MAX_FUNDING_AMOUNT, ERROR_MESSAGES, EXPORT_DATE_FORMAT,
    EXPORT_FILENAME_PREFIX, STATUS_COLORS, SDGS
)

def format_currency(amount: float, include_symbol: bool = True) -> str:
    """Format USD amounts with commas and $ sign"""
    if pd.isna(amount) or amount is None:
        return "Not specified"

    if include_symbol:
        return f"{CURRENCY_SYMBOL}{amount:,.0f}"
    else:
        return f"{amount:,.0f}"

def format_large_number(number: int) -> str:
    """Format large numbers with K, M, B suffixes"""
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    return bool(re.match(EMAIL_REGEX, email))

def validate_url(url: str) -> bool:
    """Validate URL format"""
    if not url:
        return True  # URLs are optional
    return bool(re.match(URL_REGEX, url))

def validate_coordinates(lat: Optional[float], lon: Optional[float]) -> Tuple[bool, str]:
    """Validate lat/lon range"""
    if lat is None and lon is None:
        return True, ""

    if lat is None or lon is None:
        return False, "Both latitude and longitude must be provided together"

    if not (LAT_MIN <= lat <= LAT_MAX):
        return False, f"Latitude must be between {LAT_MIN} and {LAT_MAX}"

    if not (LON_MIN <= lon <= LON_MAX):
        return False, f"Longitude must be between {LON_MIN} and {LON_MAX}"

    return True, ""

def validate_funding_amount(amount: Optional[float]) -> Tuple[bool, str]:
    """Validate funding amount"""
    if amount is None:
        return True, ""  # Funding is optional

    if not (MIN_FUNDING_AMOUNT <= amount <= MAX_FUNDING_AMOUNT):
        return False, ERROR_MESSAGES["funding_range"]

    return True, ""

def validate_text_length(text: str, max_length: int, field_name: str) -> Tuple[bool, str]:
    """Validate text field length"""
    if len(text) > max_length:
        return False, f"{field_name} exceeds maximum length of {max_length} characters"
    return True, ""

def validate_required_field(value: Any, field_name: str) -> Tuple[bool, str]:
    """Validate required field is not empty"""
    if not value or (isinstance(value, str) and not value.strip()):
        return False, f"{field_name} is required"
    return True, ""

def validate_project_form(form_data: Dict[str, Any]) -> List[str]:
    """Validate entire project submission form"""
    errors = []

    # Required fields
    required_fields = [
        ("project_name", "Project name"),
        ("organization_name", "Organization name"),
        ("contact_person", "Contact person"),
        ("contact_email", "Contact email"),
        ("city", "City"),
        ("country", "Country"),
        ("project_status", "Project status"),
        ("uia_region_id", "UIA region"),
        ("brief_description", "Brief description"),
        ("detailed_description", "Detailed description")
    ]

    for field, name in required_fields:
        is_valid, error = validate_required_field(form_data.get(field), name)
        if not is_valid:
            errors.append(error)

    # Email validation
    if form_data.get("contact_email") and not validate_email(form_data["contact_email"]):
        errors.append(ERROR_MESSAGES["invalid_email"])

    # Text length validation
    text_fields = [
        ("project_name", MAX_PROJECT_NAME_LENGTH, "Project name"),
        ("brief_description", MAX_BRIEF_DESCRIPTION_LENGTH, "Brief description"),
        ("detailed_description", MAX_DETAILED_DESCRIPTION_LENGTH, "Detailed description"),
        ("success_factors", MAX_SUCCESS_FACTORS_LENGTH, "Success factors"),
        ("organization_name", MAX_ORGANIZATION_NAME_LENGTH, "Organization name"),
        ("contact_person", MAX_CONTACT_PERSON_LENGTH, "Contact person")
    ]

    for field, max_len, name in text_fields:
        if form_data.get(field):
            is_valid, error = validate_text_length(form_data[field], max_len, name)
            if not is_valid:
                errors.append(error)

    # Coordinate validation
    lat = form_data.get("latitude")
    lon = form_data.get("longitude")
    if lat is not None or lon is not None:
        is_valid, error = validate_coordinates(lat, lon)
        if not is_valid:
            errors.append(error)

    # Funding validation
    funding = form_data.get("funding_needed_usd")
    if funding is not None:
        is_valid, error = validate_funding_amount(funding)
        if not is_valid:
            errors.append(error)

    # SDG validation
    if not form_data.get("sdgs") or len(form_data["sdgs"]) == 0:
        errors.append(ERROR_MESSAGES["no_sdg_selected"])

    # Image URL validation
    for url in form_data.get("image_urls", []):
        if url and not validate_url(url):
            errors.append(f"Invalid image URL: {url}")

    return errors

def generate_reference_id() -> str:
    """Generate ATLAS-YYYY-XXXXXX format reference ID"""
    current_year = datetime.now().year
    # Use timestamp for uniqueness in prototype
    timestamp = int(datetime.now().timestamp())
    sequence = str(timestamp)[-6:]  # Last 6 digits
    return f"ATLAS-{current_year}-{sequence}"

def export_to_csv(df: pd.DataFrame, filename_prefix: str = EXPORT_FILENAME_PREFIX) -> bytes:
    """Convert DataFrame to CSV bytes for download"""
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue().encode('utf-8')

def export_to_xlsx(df: pd.DataFrame, filename_prefix: str = EXPORT_FILENAME_PREFIX) -> bytes:
    """Convert DataFrame to Excel bytes for download"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Projects')
    return output.getvalue()

def get_export_filename(file_format: str, prefix: str = EXPORT_FILENAME_PREFIX) -> str:
    """Generate export filename with timestamp"""
    timestamp = datetime.now().strftime(EXPORT_DATE_FORMAT)
    return f"{prefix}_{timestamp}.{file_format}"

def get_color_for_status(status: str) -> str:
    """Return color hex for project status"""
    return STATUS_COLORS.get(status, "#6c757d")  # Default to gray

def get_color_for_sdg(sdg_id: int) -> str:
    """Return color hex for SDG"""
    return SDGS.get(sdg_id, {}).get("color", "#6c757d")

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length with suffix"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero"""
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default

def clean_string(text: str) -> str:
    """Clean and normalize string input"""
    if not text:
        return ""
    return text.strip()

def parse_coordinates(lat_str: str, lon_str: str) -> Tuple[Optional[float], Optional[float]]:
    """Parse coordinate strings to floats"""
    try:
        lat = float(lat_str) if lat_str and lat_str.strip() else None
        lon = float(lon_str) if lon_str and lon_str.strip() else None
        return lat, lon
    except (ValueError, TypeError):
        return None, None

def format_project_status_badge(status: str) -> str:
    """Format project status as colored badge (HTML)"""
    color = get_color_for_status(status)
    return f'<span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">{status}</span>'

def format_sdg_badge(sdg_id: int, include_name: bool = True) -> str:
    """Format SDG as colored badge (HTML)"""
    sdg = SDGS.get(sdg_id, {})
    color = sdg.get("color", "#6c757d")
    name = sdg.get("name", f"SDG {sdg_id}")

    if include_name:
        text = f"{sdg_id}. {name}"
    else:
        text = str(sdg_id)

    return f'<span style="background-color: {color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; margin: 2px;">{text}</span>'

def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage safely"""
    return safe_divide(part * 100, total, 0.0)

def group_requirements_by_category(requirements: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Group requirements by category"""
    grouped = {}
    for req in requirements:
        category = req.get("requirement_category", "Other")
        text = req.get("requirement_text", "")
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(text)
    return grouped

def prepare_chart_data(df: pd.DataFrame, x_col: str, y_col: str, limit: int = 10) -> pd.DataFrame:
    """Prepare data for charts with optional limiting"""
    if df.empty:
        return pd.DataFrame()

    chart_data = df.groupby(x_col)[y_col].agg(['count', 'sum']).reset_index()
    chart_data = chart_data.sort_values('count', ascending=False)

    if len(chart_data) > limit:
        top_data = chart_data.head(limit - 1)
        others_count = chart_data.iloc[limit-1:]['count'].sum()
        others_sum = chart_data.iloc[limit-1:]['sum'].sum()

        others_row = pd.DataFrame({
            x_col: ['Others'],
            'count': [others_count],
            'sum': [others_sum]
        })

        chart_data = pd.concat([top_data, others_row], ignore_index=True)

    return chart_data

def get_map_bounds(projects: List[Dict[str, Any]]) -> Optional[List[List[float]]]:
    """Calculate map bounds from project coordinates"""
    coords = []
    for project in projects:
        lat = project.get('latitude')
        lon = project.get('longitude')
        if lat is not None and lon is not None:
            coords.append([lat, lon])

    if not coords:
        return None

    lats = [coord[0] for coord in coords]
    lons = [coord[1] for coord in coords]

    return [
        [min(lats) - 1, min(lons) - 1],  # Southwest
        [max(lats) + 1, max(lons) + 1]   # Northeast
    ]

def filter_empty_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove empty/None values from dictionary"""
    return {k: v for k, v in data.items() if v is not None and v != ""}

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe download"""
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    return sanitized.strip('_')

def format_date(date_str: str, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """Format date string for display"""
    try:
        if isinstance(date_str, str):
            # Try to parse the date
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime(format_str)
        return str(date_str)
    except (ValueError, AttributeError):
        return str(date_str)

def create_success_message(message_type: str, custom_message: str = None) -> None:
    """Display success message in Streamlit"""
    from src.constants import SUCCESS_MESSAGES
    message = custom_message or SUCCESS_MESSAGES.get(message_type, "Operation completed successfully!")
    st.success(message)

def create_error_message(message_type: str, custom_message: str = None) -> None:
    """Display error message in Streamlit"""
    message = custom_message or ERROR_MESSAGES.get(message_type, "An error occurred. Please try again.")
    st.error(message)

def create_warning_message(message: str) -> None:
    """Display warning message in Streamlit"""
    st.warning(message)

def create_info_message(message: str) -> None:
    """Display info message in Streamlit"""
    st.info(message)

def is_admin_logged_in() -> bool:
    """Check if admin is logged in (session state)"""
    return st.session_state.get("admin_logged_in", False)

def set_admin_logged_in(status: bool) -> None:
    """Set admin login status in session state"""
    st.session_state["admin_logged_in"] = status

def get_session_value(key: str, default=None):
    """Get value from Streamlit session state"""
    return st.session_state.get(key, default)

def set_session_value(key: str, value) -> None:
    """Set value in Streamlit session state"""
    st.session_state[key] = value

def clear_session_state() -> None:
    """Clear all session state (for logout)"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def calculate_kpi_trend(current: float, previous: float) -> Tuple[float, str]:
    """Calculate trend percentage and direction"""
    if previous == 0:
        return 0.0, "neutral"

    change = ((current - previous) / previous) * 100

    if change > 0:
        return change, "up"
    elif change < 0:
        return abs(change), "down"
    else:
        return 0.0, "neutral"

def paginate_data(data: List[Any], page: int, items_per_page: int) -> Tuple[List[Any], int]:
    """Paginate data and return current page data and total pages"""
    total_items = len(data)
    total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    return data[start_idx:end_idx], total_pages