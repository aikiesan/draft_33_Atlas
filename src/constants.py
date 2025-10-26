"""
Constants and reference data for Atlas 3+3 application
"""

# UIA Regions mapping
UIA_REGIONS = {
    1: "Section I - Western Europe",
    2: "Section II - Middle East and Eastern Europe",
    3: "Section III - Americas",
    4: "Section IV - Oceania",
    5: "Section V - Africa"
}

# SDGs with official colors and descriptions
SDGS = {
    1: {"name": "No Poverty", "color": "#E5243B", "description": "End poverty in all its forms everywhere"},
    2: {"name": "Zero Hunger", "color": "#DDA63A", "description": "End hunger, achieve food security and improved nutrition"},
    3: {"name": "Good Health and Well-being", "color": "#4C9F38", "description": "Ensure healthy lives and promote well-being for all"},
    4: {"name": "Quality Education", "color": "#C5192D", "description": "Ensure inclusive and equitable quality education"},
    5: {"name": "Gender Equality", "color": "#FF3A21", "description": "Achieve gender equality and empower all women and girls"},
    6: {"name": "Clean Water and Sanitation", "color": "#26BDE2", "description": "Ensure availability and sustainable management of water"},
    7: {"name": "Affordable and Clean Energy", "color": "#FCC30B", "description": "Ensure access to affordable, reliable, sustainable energy"},
    8: {"name": "Decent Work and Economic Growth", "color": "#A21942", "description": "Promote sustained, inclusive economic growth"},
    9: {"name": "Industry, Innovation and Infrastructure", "color": "#FD6925", "description": "Build resilient infrastructure, promote innovation"},
    10: {"name": "Reduced Inequalities", "color": "#DD1367", "description": "Reduce inequality within and among countries"},
    11: {"name": "Sustainable Cities and Communities", "color": "#FD9D24", "description": "Make cities and human settlements sustainable"},
    12: {"name": "Responsible Consumption and Production", "color": "#BF8B2E", "description": "Ensure sustainable consumption and production patterns"},
    13: {"name": "Climate Action", "color": "#3F7E44", "description": "Take urgent action to combat climate change"},
    14: {"name": "Life Below Water", "color": "#0A97D9", "description": "Conserve and sustainably use the oceans, seas"},
    15: {"name": "Life on Land", "color": "#56C02B", "description": "Protect, restore and promote sustainable use of ecosystems"},
    16: {"name": "Peace, Justice and Strong Institutions", "color": "#00689D", "description": "Promote peaceful and inclusive societies"},
    17: {"name": "Partnerships for the Goals", "color": "#19486A", "description": "Strengthen means of implementation and partnerships"}
}

# Project typologies
PROJECT_TYPOLOGIES = [
    "Residential",
    "Commercial & Mixed-Use",
    "Hospitality & Tourism",
    "Educational",
    "Healthcare",
    "Civic & Government",
    "Cultural & Heritage",
    "Sports & Recreation",
    "Industrial & Logistics",
    "Infrastructure & Utilities",
    "Public Realm & Urban Landscape",
    "Natural Environment & Ecological Projects",
    "Traditional Markets & Bazaars",
    "Other"
]

# Project requirements by category
PROJECT_REQUIREMENTS_FUNDING = [
    "Private Investment / Corporate Sponsorship",
    "Public Funding / Government Grants",
    "International Aid / Development Grants",
    "Community Funding / Crowdfunding",
    "Philanthropic Support"
]

PROJECT_REQUIREMENTS_GOVERNMENT = [
    "National Government Support & Political Will",
    "Regional / Gubernatorial Support",
    "Local / Municipal Support & Endorsement",
    "Favorable Policies or Regulations",
    "Streamlined Permitting & Approval Process"
]

PROJECT_REQUIREMENTS_OTHER = [
    "Strong Project Leadership & Management",
    "Media Coverage & Public Awareness",
    "Availability of Land / Site",
    "Other"
]

# All requirements combined
PROJECT_REQUIREMENTS = {
    "Funding & Financial": PROJECT_REQUIREMENTS_FUNDING,
    "Government & Regulatory": PROJECT_REQUIREMENTS_GOVERNMENT,
    "Other": PROJECT_REQUIREMENTS_OTHER
}

# Project status options
PROJECT_STATUSES = ["Planned", "In Progress", "Implemented"]

# Workflow status options
WORKFLOW_STATUSES = ["submitted", "in_review", "approved", "rejected", "changes_requested"]

# PostgreSQL Enum Mappings (matching database schema)
PROJECT_STATUS_ENUM_VALUES = {
    "Planned": "Planned",
    "In Progress": "In Progress",
    "Implemented": "Implemented"
}

WORKFLOW_STATUS_ENUM_VALUES = {
    "submitted": "submitted",
    "in_review": "in_review",
    "approved": "approved",
    "rejected": "rejected",
    "changes_requested": "changes_requested"
}

USER_ROLE_ENUM_VALUES = {
    "public_visitor": "public_visitor",
    "submitter": "submitter",
    "reviewer": "reviewer",
    "admin": "admin",
    "manager": "manager",
    "editor": "editor"
}

REQUIREMENT_CATEGORY_ENUM_VALUES = {
    "funding": "funding",
    "government_regulatory": "government_regulatory",
    "other": "other"
}

# Status colors for UI
STATUS_COLORS = {
    "Planned": "#808080",        # Gray
    "In Progress": "#FFC107",    # Yellow/Amber
    "Implemented": "#28A745",    # Green
    "submitted": "#17A2B8",      # Blue
    "in_review": "#FFC107",      # Yellow
    "approved": "#28A745",       # Green
    "rejected": "#DC3545",       # Red
    "changes_requested": "#FD7E14"  # Orange
}

# Currency formatting
CURRENCY_SYMBOL = "$"
CURRENCY_CODE = "USD"

# Default map settings
DEFAULT_MAP_CENTER = [20.0, 0.0]  # Center of world map
DEFAULT_MAP_ZOOM = 2

# Application metadata
APP_NAME = "Atlas 3+3"
APP_TAGLINE = "A curated atlas of sustainable development projects"
APP_DESCRIPTION = """
Atlas 3+3 is a comprehensive platform showcasing innovative sustainable development projects
from around the world. Our mission is to connect ideas, inspire action, and foster
collaboration for a more sustainable future.
"""

# Contact information
CONTACT_EMAIL = "info@atlas33.org"
CONTACT_PHONE = "+1 (555) 123-4567"
PRIVACY_POLICY_URL = "https://atlas33.org/privacy"
TERMS_OF_SERVICE_URL = "https://atlas33.org/terms"

# Pagination settings
PROJECTS_PER_PAGE = 10
ADMIN_QUEUE_PER_PAGE = 20

# Form validation constants
MAX_PROJECT_NAME_LENGTH = 200
MAX_BRIEF_DESCRIPTION_LENGTH = 255
MAX_DETAILED_DESCRIPTION_LENGTH = 5000
MAX_SUCCESS_FACTORS_LENGTH = 2000
MAX_ORGANIZATION_NAME_LENGTH = 200
MAX_CONTACT_PERSON_LENGTH = 100
MIN_FUNDING_AMOUNT = 0
MAX_FUNDING_AMOUNT = 999999999.99
LAT_MIN = -90.0
LAT_MAX = 90.0
LON_MIN = -180.0
LON_MAX = 180.0

# Email validation regex
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# URL validation regex
URL_REGEX = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w))*)?$'

# Chart colors (for consistent theming)
CHART_COLORS = [
    "#0066FF",  # Primary blue
    "#FF6B6B",  # Red
    "#4ECDC4",  # Teal
    "#45B7D1",  # Light blue
    "#96CEB4",  # Light green
    "#FFEAA7",  # Light yellow
    "#DDA0DD",  # Plum
    "#98D8C8",  # Mint
    "#F7DC6F",  # Pale yellow
    "#BB8FCE",  # Light purple
    "#85C1E9",  # Sky blue
    "#F8C471",  # Peach
    "#82E0AA",  # Light green
    "#F1948A",  # Salmon
    "#85C1E9",  # Light blue
    "#D7DBDD",  # Light gray
    "#AED6F1"   # Pale blue
]

# Export file settings
EXPORT_DATE_FORMAT = "%Y%m%d_%H%M%S"
EXPORT_FILENAME_PREFIX = "atlas_projects"

# Image placeholder URLs (for demo/development)
PLACEHOLDER_IMAGES = {
    "project": "https://via.placeholder.com/800x400/0066FF/ffffff?text=Project+Image",
    "logo": "https://via.placeholder.com/200x100/0066FF/ffffff?text=Atlas+3%2B3",
    "banner": "https://via.placeholder.com/1200x400/0066FF/ffffff?text=Atlas+3%2B3+Banner"
}

# Success messages
SUCCESS_MESSAGES = {
    "project_submitted": "Project submitted successfully! You will receive an email when it is reviewed.",
    "project_approved": "Project has been approved and published to the dashboard.",
    "project_rejected": "Project has been rejected.",
    "changes_requested": "Changes have been requested for this project."
}

# Error messages
ERROR_MESSAGES = {
    "invalid_email": "Please enter a valid email address.",
    "invalid_url": "Please enter a valid URL starting with http:// or https://",
    "invalid_coordinates": "Please enter valid latitude (-90 to 90) and longitude (-180 to 180).",
    "required_field": "This field is required.",
    "funding_range": f"Funding amount must be between {CURRENCY_SYMBOL}0 and {CURRENCY_SYMBOL}{MAX_FUNDING_AMOUNT:,.2f}",
    "text_too_long": "Text exceeds maximum length.",
    "no_sdg_selected": "Please select at least one SDG.",
    "database_error": "A database error occurred. Please try again.",
    "project_not_found": "Project not found.",
    "unauthorized": "You are not authorized to perform this action."
}

# Admin user credentials (for prototype - not for production!)
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "atlas2025",
    "email": "admin@atlas33.org"
}

# Notification settings (placeholder for future implementation)
NOTIFICATION_SETTINGS = {
    "email_enabled": False,  # Disabled for prototype
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email_templates": {
        "submission_received": "Your project submission has been received and is under review.",
        "project_approved": "Congratulations! Your project has been approved and published.",
        "project_rejected": "Your project submission has been rejected.",
        "changes_requested": "Please review and update your project submission."
    }
}

# Map marker icons/colors by project status
MAP_MARKER_SETTINGS = {
    "Planned": {"color": "gray", "icon": "info-sign"},
    "In Progress": {"color": "orange", "icon": "cog"},
    "Implemented": {"color": "green", "icon": "ok-sign"},
    "default": {"color": "blue", "icon": "home"}
}

# Chart configuration defaults
CHART_DEFAULTS = {
    "height": 400,
    "margin": {"l": 60, "r": 60, "t": 60, "b": 60},
    "font_family": "Arial, sans-serif",
    "font_size": 12,
    "title_font_size": 16
}

# Session state keys (to avoid typos)
SESSION_KEYS = {
    "admin_logged_in": "admin_logged_in",
    "current_filters": "current_filters",
    "selected_project": "selected_project",
    "form_data": "form_data",
    "show_drawer": "show_drawer",
    "current_page": "current_page"
}

# Version info
APP_VERSION = "1.0.0"
LAST_UPDATED = "2025-10-26"

# PostgreSQL/PostGIS Configuration
SRID_WGS84 = 4326  # World Geodetic System 1984
SRID_WEB_MERCATOR = 3857  # Web Mercator projection

# Geospatial constants
DEFAULT_SEARCH_RADIUS_KM = 50  # Default radius for proximity searches
MAX_SEARCH_RADIUS_KM = 500    # Maximum allowed radius for searches
CLUSTERING_DISTANCE_THRESHOLD = 0.01  # Degrees for map clustering

# Database-specific settings
MATERIALIZED_VIEW_REFRESH_INTERVAL = 3600  # Seconds (1 hour)
MAX_QUERY_RESULTS = 10000  # Maximum results per query
DEFAULT_PAGINATION_SIZE = 20

# Enhanced typology codes for PostgreSQL schema
TYPOLOGY_CODES = {
    "Residential": "RESIDENTIAL",
    "Commercial & Mixed-Use": "COMMERCIAL_MIXED",
    "Hospitality & Tourism": "HOSPITALITY_TOURISM",
    "Educational": "EDUCATIONAL",
    "Healthcare": "HEALTHCARE",
    "Civic & Government": "CIVIC_GOVERNMENT",
    "Cultural & Heritage": "CULTURAL_HERITAGE",
    "Sports & Recreation": "SPORTS_RECREATION",
    "Industrial & Logistics": "INDUSTRIAL_LOGISTICS",
    "Infrastructure & Utilities": "INFRASTRUCTURE_UTILITIES",
    "Public Realm & Urban Landscape": "PUBLIC_REALM_URBAN",
    "Natural Environment & Ecological Projects": "NATURAL_ENVIRONMENT",
    "Traditional Markets & Bazaars": "TRADITIONAL_MARKETS",
    "Other": "OTHER"
}

# Enhanced requirement codes for PostgreSQL schema
REQUIREMENT_CODES = {
    # Funding & Financial
    "Private Investment / Corporate Sponsorship": "FUNDING_PRIVATE_INVESTMENT",
    "Public Funding / Government Grants": "FUNDING_PUBLIC_GRANTS",
    "International Aid / Development Grants": "FUNDING_INTERNATIONAL_AID",
    "Community Funding / Crowdfunding": "FUNDING_COMMUNITY_CROWDFUNDING",
    "Philanthropic Support": "FUNDING_PHILANTHROPIC",

    # Government & Regulatory
    "National Government Support & Political Will": "GOV_NATIONAL_SUPPORT",
    "Regional / Gubernatorial Support": "GOV_REGIONAL_SUPPORT",
    "Local / Municipal Support & Endorsement": "GOV_LOCAL_SUPPORT",
    "Favorable Policies or Regulations": "GOV_FAVORABLE_POLICIES",
    "Streamlined Permitting & Approval Process": "GOV_STREAMLINED_PERMITS",

    # Other
    "Strong Project Leadership & Management": "OTHER_STRONG_LEADERSHIP",
    "Media Coverage & Public Awareness": "OTHER_MEDIA_COVERAGE",
    "Availability of Land / Site": "OTHER_LAND_AVAILABILITY",
    "Other": "OTHER_CUSTOM"
}

# SQL Templates for materialized views
MATERIALIZED_VIEW_SQL = {
    "funding_by_region": """
    SELECT
        r.region_id,
        r.region_name,
        r.region_code,
        COUNT(p.project_id) as project_count,
        SUM(p.funding_needed_usd) as total_funding_needed,
        SUM(p.funding_spent_usd) as total_funding_spent,
        AVG(p.funding_needed_usd) as avg_funding_needed
    FROM uia_regions r
    LEFT JOIN projects p ON r.region_id = p.region_id
        AND p.deleted_at IS NULL
        AND p.workflow_status = 'approved'
    GROUP BY r.region_id, r.region_name, r.region_code
    """,

    "sdg_distribution": """
    SELECT
        s.sdg_id,
        s.sdg_number,
        s.sdg_name,
        s.sdg_short_name,
        s.sdg_color_hex,
        COUNT(ps.project_id) as project_count
    FROM sdgs s
    LEFT JOIN project_sdgs ps ON s.sdg_id = ps.sdg_id
    LEFT JOIN projects p ON ps.project_id = p.project_id
        AND p.deleted_at IS NULL
        AND p.workflow_status = 'approved'
    GROUP BY s.sdg_id, s.sdg_number, s.sdg_name, s.sdg_short_name, s.sdg_color_hex
    ORDER BY s.sdg_number
    """
}

# Advanced search configuration
FULL_TEXT_SEARCH_CONFIG = "english"  # PostgreSQL text search configuration
SEARCH_RANK_WEIGHTS = {
    "project_name": "A",        # Highest weight
    "brief_description": "B",   # High weight
    "detailed_description": "C", # Medium weight
    "organization_name": "D"     # Lower weight
}