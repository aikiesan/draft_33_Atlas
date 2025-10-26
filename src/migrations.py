"""
Migration tools for Atlas 3+3 application
Handles data migration from SQLite to PostgreSQL and schema versioning
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from tqdm import tqdm

from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from src.config import get_config, DatabaseType
from src.database import AtlasDB
from src.database_postgres import AtlasPostgreSQLDB
from src.models_postgres import (
    Base, Project, User, UiaRegion, Sdg, ProjectSdg, ProjectTypology,
    ProjectRequirement, ProjectImage, ProjectWorkflowHistory, Review,
    Typology, Requirement
)
from src.constants import TYPOLOGY_CODES, REQUIREMENT_CODES

logger = logging.getLogger(__name__)

class MigrationManager:
    """Manages database migrations and data transfers"""

    def __init__(self):
        self.config = get_config()
        self.sqlite_db = None
        self.postgres_db = None
        self.migration_log = []

    def setup_databases(self, sqlite_path: str = None, postgres_config: Dict = None):
        """Setup source SQLite and target PostgreSQL databases"""
        try:
            # Setup SQLite (source)
            if sqlite_path:
                self.sqlite_db = AtlasDB(sqlite_path)
            else:
                # Use existing SQLite database
                from src.database_interface import get_cached_database
                cached_db = get_cached_database()
                if hasattr(cached_db, 'db'):  # It's an adapter
                    self.sqlite_db = cached_db.db
                else:
                    raise ValueError("No SQLite database available for migration")

            # Setup PostgreSQL (target)
            if postgres_config:
                # Create temporary config for PostgreSQL
                temp_config = self.config
                temp_config.database.db_type = DatabaseType.POSTGRESQL
                temp_config.database.connection_string = postgres_config['connection_string']
                self.postgres_db = AtlasPostgreSQLDB(temp_config)
            else:
                # Use configured PostgreSQL database
                if self.config.database.is_postgresql:
                    self.postgres_db = AtlasPostgreSQLDB(self.config)
                else:
                    raise ValueError("PostgreSQL configuration required for migration")

            logger.info("Migration databases setup completed")
            return True

        except Exception as e:
            logger.error(f"Failed to setup migration databases: {e}")
            return False

    def validate_migration_readiness(self) -> Tuple[bool, List[str]]:
        """Validate that migration can proceed"""
        issues = []

        try:
            # Check SQLite database
            if not self.sqlite_db:
                issues.append("SQLite database not available")
            else:
                # Test SQLite connection
                try:
                    conn = self.sqlite_db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM projects")
                    project_count = cursor.fetchone()[0]
                    conn.close()

                    if project_count == 0:
                        issues.append("No projects found in SQLite database")
                    else:
                        logger.info(f"Found {project_count} projects in SQLite database")

                except Exception as e:
                    issues.append(f"SQLite database error: {e}")

            # Check PostgreSQL database
            if not self.postgres_db:
                issues.append("PostgreSQL database not available")
            else:
                # Test PostgreSQL connection
                if not self.postgres_db.health_check():
                    issues.append("PostgreSQL health check failed")

                # Check if PostgreSQL is empty (avoid overwriting data)
                try:
                    with self.postgres_db.get_session() as session:
                        existing_projects = session.query(Project).count()
                        if existing_projects > 0:
                            issues.append(f"PostgreSQL database already contains {existing_projects} projects")

                except Exception as e:
                    issues.append(f"PostgreSQL database error: {e}")

            return len(issues) == 0, issues

        except Exception as e:
            issues.append(f"Validation error: {e}")
            return False, issues

    def migrate_reference_data(self) -> bool:
        """Migrate reference data (UIA regions, SDGs, typologies, requirements)"""
        try:
            logger.info("Migrating reference data...")

            with self.postgres_db.get_session() as session:
                # Reference data is already populated during PostgreSQL initialization
                # Verify it exists
                regions_count = session.query(UiaRegion).count()
                sdgs_count = session.query(Sdg).count()
                typologies_count = session.query(Typology).count()
                requirements_count = session.query(Requirement).count()

                logger.info(f"Reference data verified: {regions_count} regions, {sdgs_count} SDGs, "
                          f"{typologies_count} typologies, {requirements_count} requirements")

                if regions_count < 5 or sdgs_count < 17:
                    logger.warning("Incomplete reference data detected")
                    return False

            self.migration_log.append("Reference data migration completed")
            return True

        except Exception as e:
            logger.error(f"Failed to migrate reference data: {e}")
            self.migration_log.append(f"Reference data migration failed: {e}")
            return False

    def migrate_users(self) -> bool:
        """Migrate users from SQLite to PostgreSQL"""
        try:
            logger.info("Migrating users...")

            # Get users from SQLite
            sqlite_conn = self.sqlite_db.get_connection()
            users_df = pd.read_sql("SELECT * FROM users", sqlite_conn)
            sqlite_conn.close()

            if users_df.empty:
                logger.warning("No users found in SQLite database")
                return True

            user_id_mapping = {}  # Map SQLite IDs to PostgreSQL UUIDs

            with self.postgres_db.get_session() as session:
                for _, sqlite_user in tqdm(users_df.iterrows(), total=len(users_df), desc="Migrating users"):
                    # Create PostgreSQL user
                    pg_user = User(
                        email=sqlite_user['email'],
                        full_name=sqlite_user.get('contact_person', sqlite_user['email']),
                        role='admin' if sqlite_user.get('is_admin') else 'submitter',
                        organization_affiliation=sqlite_user.get('organization_name'),
                        is_active=True
                    )

                    session.add(pg_user)
                    session.flush()  # Get the UUID

                    # Store mapping for project migration
                    user_id_mapping[sqlite_user['id']] = pg_user.user_id

                session.commit()

            self.user_id_mapping = user_id_mapping
            logger.info(f"Migrated {len(users_df)} users successfully")
            self.migration_log.append(f"Migrated {len(users_df)} users")
            return True

        except Exception as e:
            logger.error(f"Failed to migrate users: {e}")
            self.migration_log.append(f"User migration failed: {e}")
            return False

    def migrate_projects(self) -> bool:
        """Migrate projects and related data from SQLite to PostgreSQL"""
        try:
            logger.info("Migrating projects...")

            # Get projects from SQLite
            sqlite_conn = self.sqlite_db.get_connection()
            projects_df = pd.read_sql("""
                SELECT p.*, ur.name as region_name
                FROM projects p
                LEFT JOIN uia_regions ur ON p.uia_region_id = ur.id
            """, sqlite_conn)

            if projects_df.empty:
                logger.warning("No projects found in SQLite database")
                return True

            project_id_mapping = {}  # Map SQLite IDs to PostgreSQL UUIDs

            with self.postgres_db.get_session() as session:
                for _, sqlite_project in tqdm(projects_df.iterrows(), total=len(projects_df), desc="Migrating projects"):
                    try:
                        # Create PostgreSQL project
                        pg_project = Project(
                            project_name=sqlite_project['project_name'],
                            project_slug=self._generate_slug(sqlite_project['project_name'], session),
                            organization_name=sqlite_project['organization_name'],
                            contact_person=sqlite_project['contact_person'],
                            contact_email=sqlite_project['contact_email'],
                            project_status=sqlite_project['project_status'],
                            city=sqlite_project['city'],
                            country=sqlite_project['country'],
                            region_id=sqlite_project['uia_region_id'],
                            latitude=float(sqlite_project['latitude']) if sqlite_project['latitude'] else None,
                            longitude=float(sqlite_project['longitude']) if sqlite_project['longitude'] else None,
                            funding_needed_usd=float(sqlite_project['funding_needed_usd']) if sqlite_project['funding_needed_usd'] else None,
                            brief_description=sqlite_project['brief_description'],
                            detailed_description=sqlite_project['detailed_description'],
                            success_factors=sqlite_project.get('success_factors'),
                            workflow_status=sqlite_project['workflow_status'],
                            submission_date=self._parse_datetime(sqlite_project.get('created_at')),
                            created_by_user_id=self.user_id_mapping.get(sqlite_project.get('submitted_by')),
                            created_at=self._parse_datetime(sqlite_project.get('created_at')),
                            updated_at=self._parse_datetime(sqlite_project.get('updated_at'))
                        )

                        # Set approval/published dates for approved projects
                        if pg_project.workflow_status == 'approved':
                            pg_project.approval_date = pg_project.updated_at
                            pg_project.published_date = pg_project.updated_at

                        session.add(pg_project)
                        session.flush()  # Get the UUID

                        # Store mapping for related data migration
                        project_id_mapping[sqlite_project['id']] = pg_project.project_id

                    except Exception as e:
                        logger.error(f"Failed to migrate project {sqlite_project['project_name']}: {e}")
                        continue

                session.commit()

            self.project_id_mapping = project_id_mapping
            logger.info(f"Migrated {len(project_id_mapping)} projects successfully")
            self.migration_log.append(f"Migrated {len(project_id_mapping)} projects")

            # Migrate related data
            self._migrate_project_sdgs(sqlite_conn)
            self._migrate_project_typologies(sqlite_conn)
            self._migrate_project_requirements(sqlite_conn)
            self._migrate_project_images(sqlite_conn)
            self._migrate_workflow_history(sqlite_conn)

            sqlite_conn.close()
            return True

        except Exception as e:
            logger.error(f"Failed to migrate projects: {e}")
            self.migration_log.append(f"Project migration failed: {e}")
            return False

    def _migrate_project_sdgs(self, sqlite_conn):
        """Migrate project-SDG relationships"""
        try:
            sdgs_df = pd.read_sql("SELECT * FROM project_sdgs", sqlite_conn)

            with self.postgres_db.get_session() as session:
                for _, sqlite_sdg in tqdm(sdgs_df.iterrows(), total=len(sdgs_df), desc="Migrating project SDGs"):
                    sqlite_project_id = sqlite_sdg['project_id']
                    pg_project_id = self.project_id_mapping.get(sqlite_project_id)

                    if pg_project_id:
                        pg_project_sdg = ProjectSdg(
                            project_id=pg_project_id,
                            sdg_id=sqlite_sdg['sdg_id']
                        )
                        session.add(pg_project_sdg)

                session.commit()

            logger.info(f"Migrated {len(sdgs_df)} project-SDG relationships")

        except Exception as e:
            logger.error(f"Failed to migrate project SDGs: {e}")

    def _migrate_project_typologies(self, sqlite_conn):
        """Migrate project typologies"""
        try:
            typologies_df = pd.read_sql("SELECT * FROM project_typologies", sqlite_conn)

            with self.postgres_db.get_session() as session:
                for _, sqlite_typology in tqdm(typologies_df.iterrows(), total=len(typologies_df), desc="Migrating project typologies"):
                    sqlite_project_id = sqlite_typology['project_id']
                    pg_project_id = self.project_id_mapping.get(sqlite_project_id)

                    if pg_project_id:
                        typology_name = sqlite_typology['typology']
                        typology_code = TYPOLOGY_CODES.get(typology_name, 'OTHER')

                        pg_project_typology = ProjectTypology(
                            project_id=pg_project_id,
                            typology_code=typology_code
                        )
                        session.add(pg_project_typology)

                session.commit()

            logger.info(f"Migrated {len(typologies_df)} project typologies")

        except Exception as e:
            logger.error(f"Failed to migrate project typologies: {e}")

    def _migrate_project_requirements(self, sqlite_conn):
        """Migrate project requirements"""
        try:
            requirements_df = pd.read_sql("SELECT * FROM project_requirements", sqlite_conn)

            with self.postgres_db.get_session() as session:
                for _, sqlite_req in tqdm(requirements_df.iterrows(), total=len(requirements_df), desc="Migrating project requirements"):
                    sqlite_project_id = sqlite_req['project_id']
                    pg_project_id = self.project_id_mapping.get(sqlite_project_id)

                    if pg_project_id:
                        req_text = sqlite_req['requirement_text']
                        req_code = REQUIREMENT_CODES.get(req_text, 'OTHER_CUSTOM')

                        # Map category
                        category = sqlite_req['requirement_category']
                        if 'Funding' in category or 'Financial' in category:
                            category_enum = 'funding'
                        elif 'Government' in category or 'Regulatory' in category:
                            category_enum = 'government_regulatory'
                        else:
                            category_enum = 'other'

                        pg_project_requirement = ProjectRequirement(
                            project_id=pg_project_id,
                            requirement_code=req_code,
                            requirement_category=category_enum
                        )
                        session.add(pg_project_requirement)

                session.commit()

            logger.info(f"Migrated {len(requirements_df)} project requirements")

        except Exception as e:
            logger.error(f"Failed to migrate project requirements: {e}")

    def _migrate_project_images(self, sqlite_conn):
        """Migrate project images"""
        try:
            images_df = pd.read_sql("SELECT * FROM project_images", sqlite_conn)

            with self.postgres_db.get_session() as session:
                for _, sqlite_image in tqdm(images_df.iterrows(), total=len(images_df), desc="Migrating project images"):
                    sqlite_project_id = sqlite_image['project_id']
                    pg_project_id = self.project_id_mapping.get(sqlite_project_id)

                    if pg_project_id:
                        pg_project_image = ProjectImage(
                            project_id=pg_project_id,
                            image_url=sqlite_image['image_url'],
                            image_alt_text=sqlite_image.get('alt_text', ''),
                            display_order=0,  # Default order
                            uploaded_at=self._parse_datetime(sqlite_image.get('created_at'))
                        )
                        session.add(pg_project_image)

                session.commit()

            logger.info(f"Migrated {len(images_df)} project images")

        except Exception as e:
            logger.error(f"Failed to migrate project images: {e}")

    def _migrate_workflow_history(self, sqlite_conn):
        """Migrate workflow history"""
        try:
            history_df = pd.read_sql("SELECT * FROM project_workflow_history", sqlite_conn)

            with self.postgres_db.get_session() as session:
                for _, sqlite_history in tqdm(history_df.iterrows(), total=len(history_df), desc="Migrating workflow history"):
                    sqlite_project_id = sqlite_history['project_id']
                    pg_project_id = self.project_id_mapping.get(sqlite_project_id)
                    pg_user_id = self.user_id_mapping.get(sqlite_history.get('changed_by'))

                    if pg_project_id and pg_user_id:
                        pg_workflow_history = ProjectWorkflowHistory(
                            project_id=pg_project_id,
                            workflow_from=sqlite_history.get('old_status'),
                            workflow_to=sqlite_history['new_status'],
                            changed_by_user_id=pg_user_id,
                            reason_notes=sqlite_history.get('reason'),
                            changed_at=self._parse_datetime(sqlite_history.get('created_at'))
                        )
                        session.add(pg_workflow_history)

                session.commit()

            logger.info(f"Migrated {len(history_df)} workflow history records")

        except Exception as e:
            logger.error(f"Failed to migrate workflow history: {e}")

    def perform_full_migration(self) -> bool:
        """Perform complete migration from SQLite to PostgreSQL"""
        try:
            logger.info("Starting full migration from SQLite to PostgreSQL...")

            # Validate readiness
            is_ready, issues = self.validate_migration_readiness()
            if not is_ready:
                logger.error("Migration validation failed:")
                for issue in issues:
                    logger.error(f"  - {issue}")
                return False

            # Perform migration steps
            steps = [
                ("Reference data", self.migrate_reference_data),
                ("Users", self.migrate_users),
                ("Projects and related data", self.migrate_projects),
            ]

            for step_name, step_function in steps:
                logger.info(f"Starting: {step_name}")
                if not step_function():
                    logger.error(f"Migration failed at step: {step_name}")
                    return False
                logger.info(f"Completed: {step_name}")

            # Refresh materialized views
            logger.info("Refreshing materialized views...")
            self.postgres_db._refresh_materialized_views()

            # Final validation
            self._validate_migration_results()

            logger.info("Full migration completed successfully!")
            self.migration_log.append("Full migration completed successfully")
            return True

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            self.migration_log.append(f"Migration failed: {e}")
            return False

    def _validate_migration_results(self):
        """Validate migration results"""
        try:
            logger.info("Validating migration results...")

            # Count records in both databases
            sqlite_conn = self.sqlite_db.get_connection()
            sqlite_projects = pd.read_sql("SELECT COUNT(*) as count FROM projects", sqlite_conn).iloc[0]['count']
            sqlite_users = pd.read_sql("SELECT COUNT(*) as count FROM users", sqlite_conn).iloc[0]['count']
            sqlite_conn.close()

            with self.postgres_db.get_session() as session:
                pg_projects = session.query(Project).count()
                pg_users = session.query(User).count()

            logger.info(f"Migration validation:")
            logger.info(f"  Projects: SQLite={sqlite_projects}, PostgreSQL={pg_projects}")
            logger.info(f"  Users: SQLite={sqlite_users}, PostgreSQL={pg_users}")

            if sqlite_projects != pg_projects:
                logger.warning(f"Project count mismatch: {sqlite_projects} vs {pg_projects}")

            if sqlite_users != pg_users:
                logger.warning(f"User count mismatch: {sqlite_users} vs {pg_users}")

        except Exception as e:
            logger.error(f"Validation failed: {e}")

    def _generate_slug(self, project_name: str, session) -> str:
        """Generate unique project slug"""
        import re
        base_slug = re.sub(r'[^a-zA-Z0-9\s-]', '', project_name.lower())
        base_slug = re.sub(r'\s+', '-', base_slug.strip())

        slug = base_slug[:80]  # Limit length
        counter = 1

        while session.query(Project).filter_by(project_slug=slug).first():
            slug = f"{base_slug[:70]}-{counter}"
            counter += 1

        return slug

    def _parse_datetime(self, date_str):
        """Parse datetime string from SQLite"""
        if not date_str:
            return datetime.now(timezone.utc)

        try:
            # Try different datetime formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d']:
                try:
                    dt = datetime.strptime(str(date_str), fmt)
                    return dt.replace(tzinfo=timezone.utc)
                except ValueError:
                    continue

            # If all formats fail, return current time
            logger.warning(f"Could not parse datetime: {date_str}")
            return datetime.now(timezone.utc)

        except Exception as e:
            logger.warning(f"Datetime parsing error for '{date_str}': {e}")
            return datetime.now(timezone.utc)

    def get_migration_summary(self) -> Dict[str, Any]:
        """Get migration summary report"""
        return {
            'migration_log': self.migration_log,
            'timestamp': datetime.now().isoformat(),
            'source_database': 'SQLite',
            'target_database': 'PostgreSQL',
            'success': len([log for log in self.migration_log if 'failed' not in log.lower()]) > 0
        }

def run_migration(sqlite_path: str = None, postgres_config: Dict = None) -> bool:
    """Convenience function to run full migration"""
    migration_manager = MigrationManager()

    if not migration_manager.setup_databases(sqlite_path, postgres_config):
        logger.error("Failed to setup databases for migration")
        return False

    success = migration_manager.perform_full_migration()

    # Print summary
    summary = migration_manager.get_migration_summary()
    logger.info("Migration Summary:")
    for log_entry in summary['migration_log']:
        logger.info(f"  - {log_entry}")

    return success

if __name__ == "__main__":
    # Example usage
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Atlas 3+3 Database Migration Tool")
    parser.add_argument("--sqlite-path", help="Path to SQLite database file")
    parser.add_argument("--postgres-url", help="PostgreSQL connection URL")
    parser.add_argument("--validate-only", action="store_true", help="Only validate migration readiness")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    try:
        migration_manager = MigrationManager()

        postgres_config = None
        if args.postgres_url:
            postgres_config = {'connection_string': args.postgres_url}

        if not migration_manager.setup_databases(args.sqlite_path, postgres_config):
            print("❌ Failed to setup databases")
            sys.exit(1)

        if args.validate_only:
            is_ready, issues = migration_manager.validate_migration_readiness()
            if is_ready:
                print("✅ Migration validation passed")
                sys.exit(0)
            else:
                print("❌ Migration validation failed:")
                for issue in issues:
                    print(f"  - {issue}")
                sys.exit(1)

        # Run full migration
        success = migration_manager.perform_full_migration()

        if success:
            print("✅ Migration completed successfully")
            sys.exit(0)
        else:
            print("❌ Migration failed")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️  Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Migration error: {e}")
        sys.exit(1)