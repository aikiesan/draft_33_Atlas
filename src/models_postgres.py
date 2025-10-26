"""
SQLAlchemy models for PostgreSQL database schema
Includes PostGIS geography types, UUIDs, enums, and materialized views
"""

from sqlalchemy import (
    Column, String, Integer, Numeric, Text, Boolean, DateTime, Enum,
    ForeignKey, Index, CheckConstraint, UniqueConstraint, text
)
from sqlalchemy.dialects.postgresql import UUID, ENUM as PgEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geography
from datetime import datetime, timezone
import uuid

Base = declarative_base()

# PostgreSQL Enums
project_status_enum = PgEnum(
    'Planned', 'In Progress', 'Implemented',
    name='project_status_enum'
)

workflow_status_enum = PgEnum(
    'submitted', 'in_review', 'approved', 'rejected', 'changes_requested',
    name='workflow_status_enum'
)

user_role_enum = PgEnum(
    'public_visitor', 'submitter', 'reviewer', 'admin', 'manager', 'editor',
    name='user_role_enum'
)

requirement_category_enum = PgEnum(
    'funding', 'government_regulatory', 'other',
    name='requirement_category_enum'
)

class UiaRegion(Base):
    """UIA Regions reference table"""
    __tablename__ = 'uia_regions'

    region_id = Column(Integer, primary_key=True, autoincrement=False)
    region_name = Column(String(100), nullable=False)
    region_code = Column(String(10), nullable=False, unique=True)
    region_description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    projects = relationship("Project", back_populates="region")

    __table_args__ = (
        CheckConstraint('region_id BETWEEN 1 AND 5', name='valid_region_id'),
    )

class Sdg(Base):
    """SDGs reference table"""
    __tablename__ = 'sdgs'

    sdg_id = Column(Integer, primary_key=True)
    sdg_number = Column(Integer, nullable=False, unique=True)
    sdg_name = Column(String(255), nullable=False)
    sdg_short_name = Column(String(100))
    sdg_color_hex = Column(String(7), nullable=False)
    sdg_color_pantone = Column(String(20))
    sdg_icon_url = Column(String(500))
    sdg_description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project_sdgs = relationship("ProjectSdg", back_populates="sdg")

    __table_args__ = (
        CheckConstraint('sdg_number BETWEEN 1 AND 17', name='valid_sdg_number'),
        CheckConstraint("sdg_color_hex ~ '^#[0-9A-Fa-f]{6}$'", name='valid_hex_color'),
    )

class Typology(Base):
    """Project typologies reference table"""
    __tablename__ = 'typologies'

    typology_code = Column(String(50), primary_key=True)
    typology_name = Column(String(100), nullable=False)
    typology_description = Column(Text)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project_typologies = relationship("ProjectTypology", back_populates="typology")

class Requirement(Base):
    """Project requirements reference table"""
    __tablename__ = 'requirements'

    requirement_code = Column(String(50), primary_key=True)
    requirement_name = Column(String(150), nullable=False)
    requirement_category = Column(requirement_category_enum, nullable=False)
    requirement_description = Column(Text)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project_requirements = relationship("ProjectRequirement", back_populates="requirement")

class User(Base):
    """Users table"""
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True)
    full_name = Column(String(255), nullable=False)
    role = Column(user_role_enum, nullable=False, default='submitter')
    organization_affiliation = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    submitted_projects = relationship("Project", foreign_keys="Project.created_by_user_id", back_populates="created_by")
    reviewed_projects = relationship("Project", foreign_keys="Project.last_reviewed_by_user_id", back_populates="last_reviewed_by")
    workflow_changes = relationship("ProjectWorkflowHistory", back_populates="changed_by")
    reviews = relationship("Review", back_populates="reviewer")

    __table_args__ = (
        CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='valid_email'),
        Index('idx_users_email', 'email'),
        Index('idx_users_role', 'role'),
        Index('idx_users_is_active', 'is_active'),
    )

class Project(Base):
    """Main projects table"""
    __tablename__ = 'projects'

    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_name = Column(String(500), nullable=False)
    project_slug = Column(String(500), nullable=False, unique=True)

    # Organization & Contact
    organization_name = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)

    # Project Status
    project_status = Column(project_status_enum, nullable=False)

    # Location & Geography
    city = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False)
    region_id = Column(Integer, ForeignKey('uia_regions.region_id'), nullable=False)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    geolocation = Column(Geography('POINT', srid=4326))

    # Funding
    funding_needed_usd = Column(Numeric(15, 2), default=0)
    funding_spent_usd = Column(Numeric(15, 2))
    currency_original = Column(String(10), default='USD')

    # Content & Descriptions
    brief_description = Column(String(255), nullable=False)
    detailed_description = Column(Text, nullable=False)
    success_factors = Column(Text)

    # Workflow & Status
    workflow_status = Column(workflow_status_enum, nullable=False, default='submitted')
    submission_date = Column(DateTime(timezone=True), server_default=func.now())
    approval_date = Column(DateTime(timezone=True))
    rejection_reason = Column(Text)
    published_date = Column(DateTime(timezone=True))

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))  # Soft delete
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    last_reviewed_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))

    # Relationships
    region = relationship("UiaRegion", back_populates="projects")
    created_by = relationship("User", foreign_keys=[created_by_user_id], back_populates="submitted_projects")
    last_reviewed_by = relationship("User", foreign_keys=[last_reviewed_by_user_id], back_populates="reviewed_projects")
    project_sdgs = relationship("ProjectSdg", back_populates="project", cascade="all, delete-orphan")
    project_typologies = relationship("ProjectTypology", back_populates="project", cascade="all, delete-orphan")
    project_requirements = relationship("ProjectRequirement", back_populates="project", cascade="all, delete-orphan")
    project_images = relationship("ProjectImage", back_populates="project", cascade="all, delete-orphan")
    workflow_history = relationship("ProjectWorkflowHistory", back_populates="project", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="project", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('latitude BETWEEN -90 AND 90', name='valid_latitude'),
        CheckConstraint('longitude BETWEEN -180 AND 180', name='valid_longitude'),
        CheckConstraint('funding_needed_usd >= 0', name='valid_funding_needed'),
        CheckConstraint('funding_spent_usd >= 0', name='valid_funding_spent'),
        CheckConstraint("contact_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='valid_email_format'),
        CheckConstraint(
            '(approval_date IS NULL OR approval_date >= submission_date) AND '
            '(published_date IS NULL OR published_date >= approval_date)',
            name='valid_workflow_dates'
        ),

        # Indexes for performance
        Index('idx_projects_workflow_status', 'workflow_status', postgresql_where=text('deleted_at IS NULL')),
        Index('idx_projects_country', 'country', postgresql_where=text('deleted_at IS NULL')),
        Index('idx_projects_city', 'city', postgresql_where=text('deleted_at IS NULL')),
        Index('idx_projects_region_id', 'region_id', postgresql_where=text('deleted_at IS NULL')),
        Index('idx_projects_published_date', 'published_date', postgresql_ops={'published_date': 'DESC'}, postgresql_where=text('deleted_at IS NULL')),
        Index('idx_projects_project_status', 'project_status', postgresql_where=text('deleted_at IS NULL')),
        Index('idx_projects_project_name', 'project_name', postgresql_using='gin', postgresql_ops={'project_name': 'gin_trgm_ops'}, postgresql_where=text('deleted_at IS NULL')),
        Index('idx_projects_slug', 'project_slug', postgresql_where=text('deleted_at IS NULL')),

        # Spatial index
        Index('idx_projects_geolocation', 'geolocation', postgresql_using='gist', postgresql_where=text('deleted_at IS NULL')),
    )

class ProjectSdg(Base):
    """Projects to SDGs junction table"""
    __tablename__ = 'project_sdgs'

    id = Column(Integer, primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False)
    sdg_id = Column(Integer, ForeignKey('sdgs.sdg_id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="project_sdgs")
    sdg = relationship("Sdg", back_populates="project_sdgs")

    __table_args__ = (
        UniqueConstraint('project_id', 'sdg_id', name='unique_project_sdg'),
        Index('idx_project_sdgs_project_id', 'project_id'),
        Index('idx_project_sdgs_sdg_id', 'sdg_id'),
    )

class ProjectTypology(Base):
    """Projects to typologies junction table"""
    __tablename__ = 'project_typologies'

    id = Column(Integer, primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False)
    typology_code = Column(String(50), ForeignKey('typologies.typology_code'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="project_typologies")
    typology = relationship("Typology", back_populates="project_typologies")

    __table_args__ = (
        UniqueConstraint('project_id', 'typology_code', name='unique_project_typology'),
        Index('idx_project_typologies_project_id', 'project_id'),
        Index('idx_project_typologies_typology_code', 'typology_code'),
    )

class ProjectRequirement(Base):
    """Projects to requirements junction table"""
    __tablename__ = 'project_requirements'

    id = Column(Integer, primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False)
    requirement_code = Column(String(50), ForeignKey('requirements.requirement_code'), nullable=False)
    requirement_category = Column(requirement_category_enum, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="project_requirements")
    requirement = relationship("Requirement", back_populates="project_requirements")

    __table_args__ = (
        UniqueConstraint('project_id', 'requirement_code', name='unique_project_requirement'),
        Index('idx_project_requirements_project_id', 'project_id'),
        Index('idx_project_requirements_requirement_code', 'requirement_code'),
        Index('idx_project_requirements_category', 'requirement_category'),
    )

class ProjectImage(Base):
    """Project images table"""
    __tablename__ = 'project_images'

    id = Column(Integer, primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False)
    image_url = Column(String(1000), nullable=False)
    image_alt_text = Column(String(500))
    display_order = Column(Integer, default=0)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="project_images")

    __table_args__ = (
        CheckConstraint('display_order >= 0', name='valid_display_order'),
        Index('idx_project_images_project_id', 'project_id'),
        Index('idx_project_images_display_order', 'project_id', 'display_order'),
    )

class ProjectWorkflowHistory(Base):
    """Project workflow history (audit log)"""
    __tablename__ = 'project_workflow_history'

    id = Column(Integer, primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False)
    workflow_from = Column(workflow_status_enum)
    workflow_to = Column(workflow_status_enum, nullable=False)
    changed_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    reason_notes = Column(Text)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="workflow_history")
    changed_by = relationship("User", back_populates="workflow_changes")

    __table_args__ = (
        CheckConstraint('workflow_from IS NULL OR workflow_from != workflow_to', name='different_workflow_states'),
        Index('idx_workflow_history_project_id', 'project_id'),
        Index('idx_workflow_history_changed_at', 'changed_at', postgresql_ops={'changed_at': 'DESC'}),
        Index('idx_workflow_history_changed_by', 'changed_by_user_id'),
    )

class Review(Base):
    """Reviews table (admin feedback)"""
    __tablename__ = 'reviews'

    review_id = Column(Integer, primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.project_id', ondelete='CASCADE'), nullable=False)
    reviewer_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    review_status = Column(workflow_status_enum, nullable=False)
    review_comments = Column(Text, nullable=False)
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")

    __table_args__ = (
        CheckConstraint("review_status IN ('approved', 'rejected', 'changes_requested')", name='valid_review_status'),
        Index('idx_reviews_project_id', 'project_id'),
        Index('idx_reviews_reviewer_id', 'reviewer_user_id'),
        Index('idx_reviews_reviewed_at', 'reviewed_at', postgresql_ops={'reviewed_at': 'DESC'}),
    )

# Materialized Views (for read-only analytics)
class MvFundingByRegion(Base):
    """Materialized view for funding by region analytics"""
    __tablename__ = 'mv_funding_by_region'

    region_id = Column(Integer, primary_key=True)
    region_name = Column(String(100))
    region_code = Column(String(10))
    project_count = Column(Integer)
    total_funding_needed = Column(Numeric(15, 2))
    total_funding_spent = Column(Numeric(15, 2))
    avg_funding_needed = Column(Numeric(15, 2))

class MvSdgDistribution(Base):
    """Materialized view for SDG distribution analytics"""
    __tablename__ = 'mv_sdg_distribution'

    sdg_id = Column(Integer, primary_key=True)
    sdg_number = Column(Integer)
    sdg_name = Column(String(255))
    sdg_short_name = Column(String(100))
    sdg_color_hex = Column(String(7))
    project_count = Column(Integer)

# Triggers (defined as SQL, not in SQLAlchemy models)
# These will be created in the database initialization

TRIGGER_FUNCTIONS = [
    """
    CREATE OR REPLACE FUNCTION update_project_geolocation()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.geolocation := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::geography;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """,

    """
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
]

TRIGGERS = [
    """
    DROP TRIGGER IF EXISTS trigger_update_geolocation ON projects;
    CREATE TRIGGER trigger_update_geolocation
    BEFORE INSERT OR UPDATE OF latitude, longitude ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_project_geolocation();
    """,

    """
    DROP TRIGGER IF EXISTS trigger_projects_updated_at ON projects;
    CREATE TRIGGER trigger_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """,

    """
    DROP TRIGGER IF EXISTS trigger_users_updated_at ON users;
    CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """
]