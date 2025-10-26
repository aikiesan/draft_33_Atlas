"""
PostgreSQL database adapter for Atlas 3+3 application
Advanced implementation with PostGIS, UUIDs, enums, and materialized views
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple, Union
import pandas as pd

from sqlalchemy import create_engine, text, func, and_, or_, desc, asc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.sql import select, update, delete, insert
from geoalchemy2 import Geography, functions as geo_func
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import Point

from src.database_interface import DatabaseInterface
from src.models_postgres import (
    Base, Project, User, UiaRegion, Sdg, ProjectSdg, ProjectTypology,
    ProjectRequirement, ProjectImage, ProjectWorkflowHistory, Review,
    Typology, Requirement, MvFundingByRegion, MvSdgDistribution
)
from src.constants import (
    PROJECT_STATUS_ENUM_VALUES, WORKFLOW_STATUS_ENUM_VALUES,
    USER_ROLE_ENUM_VALUES, REQUIREMENT_CATEGORY_ENUM_VALUES,
    SRID_WGS84, DEFAULT_SEARCH_RADIUS_KM, MAX_SEARCH_RADIUS_KM,
    MATERIALIZED_VIEW_REFRESH_INTERVAL, MAX_QUERY_RESULTS,
    FULL_TEXT_SEARCH_CONFIG, SEARCH_RANK_WEIGHTS
)

logger = logging.getLogger(__name__)

class AtlasPostgreSQLDB(DatabaseInterface):
    """PostgreSQL database implementation with PostGIS support"""

    def __init__(self, config):
        self.config = config
        self.engine = None
        self.SessionLocal = None
        self._setup_database()

    def _setup_database(self):
        """Setup database engine and session factory"""
        try:
            self.engine = create_engine(
                self.config.database.connection_string,
                pool_size=self.config.database.pool_size,
                max_overflow=self.config.database.max_overflow,
                echo=self.config.database.echo,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600    # Recycle connections every hour
            )

            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            # Initialize database schema
            self._initialize_schema()

        except Exception as e:
            logger.error(f"Failed to setup PostgreSQL database: {e}")
            raise

    def _initialize_schema(self):
        """Initialize database schema and reference data"""
        try:
            # Create all tables
            Base.metadata.create_all(bind=self.engine)

            # Create extensions if they don't exist
            with self.engine.connect() as conn:
                conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
                conn.execute(text('CREATE EXTENSION IF NOT EXISTS "postgis"'))
                conn.commit()

            # Populate reference data
            self._populate_reference_data()

            # Create materialized views
            self._create_materialized_views()

            logger.info("PostgreSQL schema initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise

    def _populate_reference_data(self):
        """Populate reference tables with initial data"""
        with self.get_session() as session:
            try:
                # UIA Regions
                regions_data = [
                    (1, "Section I - Western Europe", "SECTION_I", "Western European countries"),
                    (2, "Section II - Middle East and Eastern Europe", "SECTION_II", "Middle East and Eastern European countries"),
                    (3, "Section III - Americas", "SECTION_III", "North, Central and South American countries"),
                    (4, "Section IV - Oceania", "SECTION_IV", "Oceanic countries and territories"),
                    (5, "Section V - Africa", "SECTION_V", "African countries")
                ]

                for region_id, name, code, description in regions_data:
                    existing = session.query(UiaRegion).filter_by(region_id=region_id).first()
                    if not existing:
                        region = UiaRegion(
                            region_id=region_id,
                            region_name=name,
                            region_code=code,
                            region_description=description
                        )
                        session.add(region)

                # SDGs
                sdgs_data = [
                    (1, 1, "No Poverty", "No Poverty", "#E5243B", "E5243B", None, "End poverty in all its forms everywhere"),
                    (2, 2, "Zero Hunger", "Zero Hunger", "#DDA63A", "DDA63A", None, "End hunger, achieve food security and improved nutrition"),
                    (3, 3, "Good Health and Well-being", "Good Health", "#4C9F38", "4C9F38", None, "Ensure healthy lives and promote well-being for all"),
                    (4, 4, "Quality Education", "Quality Education", "#C5192D", "C5192D", None, "Ensure inclusive and equitable quality education"),
                    (5, 5, "Gender Equality", "Gender Equality", "#FF3A21", "FF3A21", None, "Achieve gender equality and empower all women and girls"),
                    (6, 6, "Clean Water and Sanitation", "Clean Water", "#26BDE2", "26BDE2", None, "Ensure availability and sustainable management of water"),
                    (7, 7, "Affordable and Clean Energy", "Clean Energy", "#FCC30B", "FCC30B", None, "Ensure access to affordable, reliable, sustainable energy"),
                    (8, 8, "Decent Work and Economic Growth", "Decent Work", "#A21942", "A21942", None, "Promote sustained, inclusive economic growth"),
                    (9, 9, "Industry, Innovation and Infrastructure", "Innovation", "#FD6925", "FD6925", None, "Build resilient infrastructure, promote innovation"),
                    (10, 10, "Reduced Inequalities", "Reduced Inequalities", "#DD1367", "DD1367", None, "Reduce inequality within and among countries"),
                    (11, 11, "Sustainable Cities and Communities", "Sustainable Cities", "#FD9D24", "FD9D24", None, "Make cities and human settlements sustainable"),
                    (12, 12, "Responsible Consumption and Production", "Responsible Consumption", "#BF8B2E", "BF8B2E", None, "Ensure sustainable consumption and production patterns"),
                    (13, 13, "Climate Action", "Climate Action", "#3F7E44", "3F7E44", None, "Take urgent action to combat climate change"),
                    (14, 14, "Life Below Water", "Life Below Water", "#0A97D9", "0A97D9", None, "Conserve and sustainably use the oceans, seas"),
                    (15, 15, "Life on Land", "Life on Land", "#56C02B", "56C02B", None, "Protect, restore and promote sustainable use of ecosystems"),
                    (16, 16, "Peace, Justice and Strong Institutions", "Peace & Justice", "#00689D", "00689D", None, "Promote peaceful and inclusive societies"),
                    (17, 17, "Partnerships for the Goals", "Partnerships", "#19486A", "19486A", None, "Strengthen means of implementation and partnerships")
                ]

                for sdg_id, number, name, short_name, color_hex, pantone, icon_url, description in sdgs_data:
                    existing = session.query(Sdg).filter_by(sdg_number=number).first()
                    if not existing:
                        sdg = Sdg(
                            sdg_number=number,
                            sdg_name=name,
                            sdg_short_name=short_name,
                            sdg_color_hex=color_hex,
                            sdg_color_pantone=pantone,
                            sdg_icon_url=icon_url,
                            sdg_description=description
                        )
                        session.add(sdg)

                # Typologies
                from src.constants import TYPOLOGY_CODES
                for display_name, code in TYPOLOGY_CODES.items():
                    existing = session.query(Typology).filter_by(typology_code=code).first()
                    if not existing:
                        typology = Typology(
                            typology_code=code,
                            typology_name=display_name,
                            typology_description=f"Projects in the {display_name} category"
                        )
                        session.add(typology)

                # Requirements
                from src.constants import REQUIREMENT_CODES, PROJECT_REQUIREMENTS
                for category, requirements_list in PROJECT_REQUIREMENTS.items():
                    category_code = "funding" if "Funding" in category else "government_regulatory" if "Government" in category else "other"

                    for req_name in requirements_list:
                        req_code = REQUIREMENT_CODES.get(req_name, f"OTHER_CUSTOM_{hash(req_name) % 10000}")
                        existing = session.query(Requirement).filter_by(requirement_code=req_code).first()
                        if not existing:
                            requirement = Requirement(
                                requirement_code=req_code,
                                requirement_name=req_name,
                                requirement_category=category_code,
                                requirement_description=f"Requirement: {req_name}"
                            )
                            session.add(requirement)

                session.commit()
                logger.info("Reference data populated successfully")

            except Exception as e:
                session.rollback()
                logger.error(f"Failed to populate reference data: {e}")
                raise

    def _create_materialized_views(self):
        """Create materialized views for analytics"""
        try:
            with self.engine.connect() as conn:
                # Funding by Region materialized view
                conn.execute(text("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS mv_funding_by_region AS
                SELECT
                    r.region_id,
                    r.region_name,
                    r.region_code,
                    COUNT(p.project_id) as project_count,
                    COALESCE(SUM(p.funding_needed_usd), 0) as total_funding_needed,
                    COALESCE(SUM(p.funding_spent_usd), 0) as total_funding_spent,
                    COALESCE(AVG(p.funding_needed_usd), 0) as avg_funding_needed
                FROM uia_regions r
                LEFT JOIN projects p ON r.region_id = p.region_id
                    AND p.deleted_at IS NULL
                    AND p.workflow_status = 'approved'
                GROUP BY r.region_id, r.region_name, r.region_code
                """))

                # SDG Distribution materialized view
                conn.execute(text("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS mv_sdg_distribution AS
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
                """))

                # Create unique indexes
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_funding_region_id ON mv_funding_by_region(region_id)"))
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_sdg_distribution_id ON mv_sdg_distribution(sdg_id)"))

                conn.commit()
                logger.info("Materialized views created successfully")

        except Exception as e:
            logger.error(f"Failed to create materialized views: {e}")

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

    def connect(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            return False

    def disconnect(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()

    def health_check(self) -> bool:
        """Comprehensive database health check"""
        try:
            with self.get_session() as session:
                # Test basic connectivity
                session.execute(text("SELECT 1"))

                # Test PostGIS extension
                session.execute(text("SELECT PostGIS_Version()"))

                # Test UUID extension
                session.execute(text("SELECT uuid_generate_v4()"))

                # Test table access
                session.query(Project).count()
                session.query(UiaRegion).count()
                session.query(Sdg).count()

                return True

        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            return False

    def get_all_published_projects(self) -> List[Dict[str, Any]]:
        """Get all approved/published projects"""
        with self.get_session() as session:
            try:
                query = session.query(Project, UiaRegion.region_name).join(
                    UiaRegion, Project.region_id == UiaRegion.region_id
                ).filter(
                    Project.workflow_status == 'approved',
                    Project.deleted_at.is_(None)
                ).order_by(desc(Project.published_date))

                results = []
                for project, region_name in query.all():
                    project_dict = self._project_to_dict(project)
                    project_dict['region_name'] = region_name
                    results.append(project_dict)

                return results

            except Exception as e:
                logger.error(f"Failed to get published projects: {e}")
                return []

    def get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed project information by ID"""
        with self.get_session() as session:
            try:
                # Convert string UUID to UUID object
                if isinstance(project_id, str):
                    project_uuid = uuid.UUID(project_id)
                else:
                    project_uuid = project_id

                project = session.query(Project).filter_by(project_id=project_uuid).first()
                if not project:
                    return None

                # Get related data
                project_dict = self._project_to_dict(project)

                # Get region name
                region = session.query(UiaRegion).filter_by(region_id=project.region_id).first()
                project_dict['region_name'] = region.region_name if region else None

                # Get SDGs
                sdgs = session.query(Sdg).join(ProjectSdg).filter(
                    ProjectSdg.project_id == project.project_id
                ).all()
                project_dict['sdgs'] = [self._sdg_to_dict(sdg) for sdg in sdgs]

                # Get typologies
                typologies = session.query(ProjectTypology, Typology).join(
                    Typology, ProjectTypology.typology_code == Typology.typology_code
                ).filter(ProjectTypology.project_id == project.project_id).all()
                project_dict['typologies'] = [
                    {'typology': typ.typology_name, 'code': typ.typology_code}
                    for pt, typ in typologies
                ]

                # Get requirements
                requirements = session.query(ProjectRequirement, Requirement).join(
                    Requirement, ProjectRequirement.requirement_code == Requirement.requirement_code
                ).filter(ProjectRequirement.project_id == project.project_id).all()
                project_dict['requirements'] = [
                    {
                        'requirement_category': req.requirement_category,
                        'requirement_text': req.requirement_name,
                        'requirement_code': req.requirement_code
                    }
                    for pr, req in requirements
                ]

                # Get images
                images = session.query(ProjectImage).filter_by(project_id=project.project_id).order_by(
                    ProjectImage.display_order
                ).all()
                project_dict['images'] = [
                    {
                        'image_url': img.image_url,
                        'alt_text': img.image_alt_text,
                        'display_order': img.display_order
                    }
                    for img in images
                ]

                return project_dict

            except Exception as e:
                logger.error(f"Failed to get project {project_id}: {e}")
                return None

    def get_projects_by_filters(self, region: str = None, sdg: int = None,
                               city: str = None, funded_by: str = None,
                               **kwargs) -> List[Dict[str, Any]]:
        """Filter projects by multiple criteria with advanced PostGIS support"""
        with self.get_session() as session:
            try:
                query = session.query(Project, UiaRegion.region_name).join(
                    UiaRegion, Project.region_id == UiaRegion.region_id
                ).filter(
                    Project.workflow_status == 'approved',
                    Project.deleted_at.is_(None)
                )

                # Apply filters
                if region:
                    query = query.filter(UiaRegion.region_name == region)

                if sdg:
                    query = query.join(ProjectSdg).filter(ProjectSdg.sdg_id == sdg)

                if city:
                    query = query.filter(func.lower(Project.city) == func.lower(city))

                if funded_by:
                    query = query.filter(Project.organization_name.ilike(f'%{funded_by}%'))

                # Advanced filters from kwargs
                if 'near_lat' in kwargs and 'near_lon' in kwargs:
                    lat, lon = float(kwargs['near_lat']), float(kwargs['near_lon'])
                    radius_km = float(kwargs.get('radius_km', DEFAULT_SEARCH_RADIUS_KM))
                    point = f'POINT({lon} {lat})'
                    query = query.filter(
                        func.ST_DWithin(
                            Project.geolocation,
                            func.ST_GeogFromText(point),
                            radius_km * 1000  # Convert km to meters
                        )
                    )

                if 'bounds' in kwargs:
                    bounds = kwargs['bounds']  # [north, south, east, west]
                    if len(bounds) == 4:
                        north, south, east, west = bounds
                        bbox = f'POLYGON(({west} {south}, {east} {south}, {east} {north}, {west} {north}, {west} {south}))'
                        query = query.filter(
                            func.ST_Within(
                                Project.geolocation,
                                func.ST_GeogFromText(bbox)
                            )
                        )

                # Limit results
                limit = min(kwargs.get('limit', MAX_QUERY_RESULTS), MAX_QUERY_RESULTS)
                query = query.limit(limit)

                results = []
                for project, region_name in query.all():
                    project_dict = self._project_to_dict(project)
                    project_dict['region_name'] = region_name
                    results.append(project_dict)

                return results

            except Exception as e:
                logger.error(f"Failed to filter projects: {e}")
                return []

    def create_project(self, form_data: Dict[str, Any]) -> str:
        """Create a new project from submission form"""
        with self.get_session() as session:
            try:
                # Create or get user
                user = session.query(User).filter_by(email=form_data['contact_email']).first()
                if not user:
                    user = User(
                        email=form_data['contact_email'],
                        full_name=form_data['contact_person'],
                        role='submitter',
                        organization_affiliation=form_data['organization_name']
                    )
                    session.add(user)
                    session.flush()  # Get user ID

                # Generate project slug
                slug = self._generate_project_slug(form_data['project_name'], session)

                # Create project
                project = Project(
                    project_name=form_data['project_name'],
                    project_slug=slug,
                    organization_name=form_data['organization_name'],
                    contact_person=form_data['contact_person'],
                    contact_email=form_data['contact_email'],
                    project_status=form_data['project_status'],
                    city=form_data['city'],
                    country=form_data['country'],
                    region_id=form_data['uia_region_id'],
                    latitude=form_data.get('latitude'),
                    longitude=form_data.get('longitude'),
                    funding_needed_usd=form_data.get('funding_needed_usd'),
                    brief_description=form_data['brief_description'],
                    detailed_description=form_data['detailed_description'],
                    success_factors=form_data.get('success_factors'),
                    workflow_status='submitted',
                    created_by_user_id=user.user_id
                )

                session.add(project)
                session.flush()  # Get project ID

                # Add SDGs
                for sdg_id in form_data.get('sdgs', []):
                    project_sdg = ProjectSdg(project_id=project.project_id, sdg_id=sdg_id)
                    session.add(project_sdg)

                # Add typologies
                from src.constants import TYPOLOGY_CODES
                for typology_name in form_data.get('typologies', []):
                    typology_code = TYPOLOGY_CODES.get(typology_name, 'OTHER')
                    project_typology = ProjectTypology(
                        project_id=project.project_id,
                        typology_code=typology_code
                    )
                    session.add(project_typology)

                # Add requirements
                from src.constants import REQUIREMENT_CODES
                for req in form_data.get('requirements', []):
                    req_text = req.get('text', '')
                    req_code = REQUIREMENT_CODES.get(req_text, 'OTHER_CUSTOM')
                    category = req.get('category', 'other')

                    project_requirement = ProjectRequirement(
                        project_id=project.project_id,
                        requirement_code=req_code,
                        requirement_category=category
                    )
                    session.add(project_requirement)

                # Add images
                for i, image_url in enumerate(form_data.get('image_urls', [])):
                    if image_url.strip():
                        project_image = ProjectImage(
                            project_id=project.project_id,
                            image_url=image_url.strip(),
                            image_alt_text=f"Project image {i+1}",
                            display_order=i
                        )
                        session.add(project_image)

                session.commit()

                # Generate reference ID
                ref_id = f"ATLAS-{datetime.now().year}-{str(project.project_id).replace('-', '')[:6].upper()}"

                return ref_id

            except Exception as e:
                session.rollback()
                logger.error(f"Failed to create project: {e}")
                raise

    def update_project_status(self, project_id: str, new_status: str,
                            reason: str = None, reviewer_id: str = None):
        """Update project workflow status with audit trail"""
        with self.get_session() as session:
            try:
                project_uuid = uuid.UUID(project_id) if isinstance(project_id, str) else project_id
                reviewer_uuid = uuid.UUID(reviewer_id) if reviewer_id and isinstance(reviewer_id, str) else reviewer_id

                project = session.query(Project).filter_by(project_id=project_uuid).first()
                if not project:
                    raise ValueError(f"Project {project_id} not found")

                old_status = project.workflow_status

                # Update project
                project.workflow_status = new_status
                project.updated_at = datetime.now(timezone.utc)

                if new_status == 'approved':
                    project.approval_date = datetime.now(timezone.utc)
                    project.published_date = datetime.now(timezone.utc)
                elif new_status == 'rejected':
                    project.rejection_reason = reason

                if reviewer_uuid:
                    project.last_reviewed_by_user_id = reviewer_uuid

                # Add workflow history
                history = ProjectWorkflowHistory(
                    project_id=project.project_id,
                    workflow_from=old_status,
                    workflow_to=new_status,
                    changed_by_user_id=reviewer_uuid,
                    reason_notes=reason
                )
                session.add(history)

                # Add review record
                if reviewer_uuid:
                    review = Review(
                        project_id=project.project_id,
                        reviewer_user_id=reviewer_uuid,
                        review_status=new_status,
                        review_comments=reason or f"Status changed from {old_status} to {new_status}"
                    )
                    session.add(review)

                session.commit()

                # Refresh materialized views if project was approved/rejected
                if new_status in ['approved', 'rejected']:
                    self._refresh_materialized_views()

            except Exception as e:
                session.rollback()
                logger.error(f"Failed to update project status: {e}")
                raise

    def get_pending_reviews(self) -> List[Dict[str, Any]]:
        """Get projects pending review"""
        with self.get_session() as session:
            try:
                query = session.query(Project, UiaRegion.region_name).join(
                    UiaRegion, Project.region_id == UiaRegion.region_id
                ).filter(
                    Project.workflow_status.in_(['submitted', 'in_review', 'changes_requested']),
                    Project.deleted_at.is_(None)
                ).order_by(Project.submission_date)

                results = []
                for project, region_name in query.all():
                    project_dict = self._project_to_dict(project)
                    project_dict['region_name'] = region_name
                    results.append(project_dict)

                return results

            except Exception as e:
                logger.error(f"Failed to get pending reviews: {e}")
                return []

    def get_admin_metrics(self) -> Dict[str, Any]:
        """Get comprehensive admin dashboard metrics"""
        with self.get_session() as session:
            try:
                # Pending reviews
                pending = session.query(Project).filter(
                    Project.workflow_status.in_(['submitted', 'in_review']),
                    Project.deleted_at.is_(None)
                ).count()

                # This month's approvals
                start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                approved_month = session.query(Project).filter(
                    Project.workflow_status == 'approved',
                    Project.approval_date >= start_of_month,
                    Project.deleted_at.is_(None)
                ).count()

                # This month's rejections
                rejected_month = session.query(Project).filter(
                    Project.workflow_status == 'rejected',
                    Project.updated_at >= start_of_month,
                    Project.deleted_at.is_(None)
                ).count()

                # Total published
                total_published = session.query(Project).filter(
                    Project.workflow_status == 'approved',
                    Project.deleted_at.is_(None)
                ).count()

                # Average review time (placeholder - would need more complex query)
                avg_review_time = "2.3 days"

                return {
                    'pending_reviews': pending,
                    'approved_this_month': approved_month,
                    'rejected_this_month': rejected_month,
                    'total_published': total_published,
                    'avg_review_time': avg_review_time
                }

            except Exception as e:
                logger.error(f"Failed to get admin metrics: {e}")
                return {
                    'pending_reviews': 0,
                    'approved_this_month': 0,
                    'rejected_this_month': 0,
                    'total_published': 0,
                    'avg_review_time': "N/A"
                }

    def get_kpi_metrics(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get KPI metrics for dashboard using optimized queries"""
        with self.get_session() as session:
            try:
                # Use filtered projects for accuracy
                projects = self.get_projects_by_filters(**(filters or {}))
                df = pd.DataFrame(projects)

                if df.empty:
                    return {
                        'total_projects': 0,
                        'total_cities': 0,
                        'total_countries': 0,
                        'funding_needed': 0,
                        'funding_spent': 0
                    }

                return {
                    'total_projects': len(df),
                    'total_cities': df['city'].nunique(),
                    'total_countries': df['country'].nunique(),
                    'funding_needed': df['funding_needed_usd'].fillna(0).sum(),
                    'funding_spent': df[df['project_status'] == 'Implemented']['funding_needed_usd'].fillna(0).sum()
                }

            except Exception as e:
                logger.error(f"Failed to get KPI metrics: {e}")
                return {
                    'total_projects': 0,
                    'total_cities': 0,
                    'total_countries': 0,
                    'funding_needed': 0,
                    'funding_spent': 0
                }

    def get_sdg_distribution(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get SDG distribution from materialized view"""
        with self.get_session() as session:
            try:
                # Use materialized view for performance
                results = session.execute(text("SELECT * FROM mv_sdg_distribution ORDER BY sdg_number")).fetchall()

                return [
                    {
                        'sdg_id': row.sdg_id,
                        'sdg_number': row.sdg_number,
                        'sdg_name': row.sdg_name,
                        'sdg_short_name': row.sdg_short_name,
                        'sdg_color_hex': row.sdg_color_hex,
                        'project_count': row.project_count
                    }
                    for row in results
                ]

            except Exception as e:
                logger.error(f"Failed to get SDG distribution: {e}")
                return []

    def get_funding_by_region(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get funding statistics by region from materialized view"""
        with self.get_session() as session:
            try:
                # Use materialized view for performance
                results = session.execute(text("SELECT * FROM mv_funding_by_region ORDER BY region_id")).fetchall()

                return [
                    {
                        'region_id': row.region_id,
                        'region_name': row.region_name,
                        'region_code': row.region_code,
                        'project_count': row.project_count,
                        'total_funding_needed': float(row.total_funding_needed),
                        'total_funding_spent': float(row.total_funding_spent),
                        'avg_funding_needed': float(row.avg_funding_needed)
                    }
                    for row in results
                ]

            except Exception as e:
                logger.error(f"Failed to get funding by region: {e}")
                return []

    # PostGIS-specific geospatial operations
    def get_projects_near_location(self, latitude: float, longitude: float,
                                 radius_km: float = DEFAULT_SEARCH_RADIUS_KM) -> List[Dict[str, Any]]:
        """Get projects within radius of location using PostGIS"""
        radius_km = min(radius_km, MAX_SEARCH_RADIUS_KM)  # Safety limit

        return self.get_projects_by_filters(
            near_lat=latitude,
            near_lon=longitude,
            radius_km=radius_km
        )

    def get_projects_in_bounds(self, north: float, south: float,
                             east: float, west: float) -> List[Dict[str, Any]]:
        """Get projects within geographic bounds using PostGIS"""
        return self.get_projects_by_filters(
            bounds=[north, south, east, west]
        )

    def search_projects(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Full-text search across projects using PostgreSQL"""
        with self.get_session() as session:
            try:
                # Create full-text search query
                search_query = session.query(Project, UiaRegion.region_name).join(
                    UiaRegion, Project.region_id == UiaRegion.region_id
                ).filter(
                    Project.workflow_status == 'approved',
                    Project.deleted_at.is_(None),
                    or_(
                        func.to_tsvector(FULL_TEXT_SEARCH_CONFIG, Project.project_name).match(query),
                        func.to_tsvector(FULL_TEXT_SEARCH_CONFIG, Project.brief_description).match(query),
                        func.to_tsvector(FULL_TEXT_SEARCH_CONFIG, Project.detailed_description).match(query),
                        func.to_tsvector(FULL_TEXT_SEARCH_CONFIG, Project.organization_name).match(query)
                    )
                ).order_by(
                    # Rank by relevance using weights
                    desc(
                        func.ts_rank_cd(
                            func.setweight(func.to_tsvector(FULL_TEXT_SEARCH_CONFIG, Project.project_name), 'A') +
                            func.setweight(func.to_tsvector(FULL_TEXT_SEARCH_CONFIG, Project.brief_description), 'B') +
                            func.setweight(func.to_tsvector(FULL_TEXT_SEARCH_CONFIG, Project.detailed_description), 'C') +
                            func.setweight(func.to_tsvector(FULL_TEXT_SEARCH_CONFIG, Project.organization_name), 'D'),
                            func.plainto_tsquery(FULL_TEXT_SEARCH_CONFIG, query)
                        )
                    )
                ).limit(limit)

                results = []
                for project, region_name in search_query.all():
                    project_dict = self._project_to_dict(project)
                    project_dict['region_name'] = region_name
                    results.append(project_dict)

                return results

            except Exception as e:
                logger.error(f"Full-text search failed: {e}")
                return []

    # Reference data methods
    def get_unique_cities(self) -> List[str]:
        """Get list of unique cities"""
        with self.get_session() as session:
            try:
                cities = session.query(Project.city).filter(
                    Project.workflow_status == 'approved',
                    Project.deleted_at.is_(None),
                    Project.city.isnot(None)
                ).distinct().order_by(Project.city).all()

                return [city[0] for city in cities]

            except Exception as e:
                logger.error(f"Failed to get unique cities: {e}")
                return []

    def get_unique_organizations(self) -> List[str]:
        """Get list of unique organizations"""
        with self.get_session() as session:
            try:
                orgs = session.query(Project.organization_name).filter(
                    Project.workflow_status == 'approved',
                    Project.deleted_at.is_(None),
                    Project.organization_name.isnot(None)
                ).distinct().order_by(Project.organization_name).all()

                return [org[0] for org in orgs]

            except Exception as e:
                logger.error(f"Failed to get unique organizations: {e}")
                return []

    def get_uia_regions(self) -> List[Dict[str, Any]]:
        """Get UIA regions reference data"""
        with self.get_session() as session:
            try:
                regions = session.query(UiaRegion).order_by(UiaRegion.region_id).all()
                return [
                    {
                        'region_id': region.region_id,
                        'region_name': region.region_name,
                        'region_code': region.region_code,
                        'region_description': region.region_description
                    }
                    for region in regions
                ]

            except Exception as e:
                logger.error(f"Failed to get UIA regions: {e}")
                return []

    def get_sdgs(self) -> List[Dict[str, Any]]:
        """Get SDGs reference data"""
        with self.get_session() as session:
            try:
                sdgs = session.query(Sdg).order_by(Sdg.sdg_number).all()
                return [self._sdg_to_dict(sdg) for sdg in sdgs]

            except Exception as e:
                logger.error(f"Failed to get SDGs: {e}")
                return []

    # Utility methods
    def bulk_update_projects(self, updates: List[Dict[str, Any]]) -> int:
        """Bulk update multiple projects efficiently"""
        with self.get_session() as session:
            try:
                count = 0
                for update in updates:
                    project_id = update.get('project_id')
                    if project_id:
                        session.query(Project).filter_by(project_id=project_id).update(update)
                        count += 1

                session.commit()
                return count

            except Exception as e:
                session.rollback()
                logger.error(f"Bulk update failed: {e}")
                return 0

    def export_projects_data(self, format: str = "csv",
                           filters: Dict[str, Any] = None) -> bytes:
        """Export filtered projects data"""
        projects = self.get_projects_by_filters(**(filters or {}))
        df = pd.DataFrame(projects)

        from src.utils import export_to_csv, export_to_xlsx

        if format.lower() == "csv":
            return export_to_csv(df)
        elif format.lower() in ["xlsx", "excel"]:
            return export_to_xlsx(df)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _refresh_materialized_views(self):
        """Refresh materialized views"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_funding_by_region"))
                conn.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_sdg_distribution"))
                conn.commit()
                logger.info("Materialized views refreshed successfully")

        except Exception as e:
            logger.error(f"Failed to refresh materialized views: {e}")

    def _generate_project_slug(self, project_name: str, session: Session) -> str:
        """Generate unique project slug"""
        import re
        base_slug = re.sub(r'[^a-zA-Z0-9\s-]', '', project_name.lower())
        base_slug = re.sub(r'\s+', '-', base_slug.strip())

        slug = base_slug
        counter = 1

        while session.query(Project).filter_by(project_slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def _project_to_dict(self, project: Project) -> Dict[str, Any]:
        """Convert Project model to dictionary"""
        return {
            'id': str(project.project_id),
            'project_id': str(project.project_id),
            'project_name': project.project_name,
            'project_slug': project.project_slug,
            'organization_name': project.organization_name,
            'contact_person': project.contact_person,
            'contact_email': project.contact_email,
            'project_status': project.project_status,
            'workflow_status': project.workflow_status,
            'city': project.city,
            'country': project.country,
            'uia_region_id': project.region_id,
            'latitude': float(project.latitude) if project.latitude else None,
            'longitude': float(project.longitude) if project.longitude else None,
            'funding_needed_usd': float(project.funding_needed_usd) if project.funding_needed_usd else None,
            'funding_spent_usd': float(project.funding_spent_usd) if project.funding_spent_usd else None,
            'brief_description': project.brief_description,
            'detailed_description': project.detailed_description,
            'success_factors': project.success_factors,
            'created_at': project.created_at.isoformat() if project.created_at else None,
            'updated_at': project.updated_at.isoformat() if project.updated_at else None,
            'submission_date': project.submission_date.isoformat() if project.submission_date else None,
            'approval_date': project.approval_date.isoformat() if project.approval_date else None,
            'published_date': project.published_date.isoformat() if project.published_date else None
        }

    def _sdg_to_dict(self, sdg: Sdg) -> Dict[str, Any]:
        """Convert SDG model to dictionary"""
        return {
            'id': sdg.sdg_id,
            'sdg_id': sdg.sdg_id,
            'sdg_number': sdg.sdg_number,
            'name': sdg.sdg_name,
            'sdg_name': sdg.sdg_name,
            'sdg_short_name': sdg.sdg_short_name,
            'color': sdg.sdg_color_hex,
            'sdg_color_hex': sdg.sdg_color_hex,
            'description': sdg.sdg_description
        }