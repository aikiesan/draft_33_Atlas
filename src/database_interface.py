"""
Abstract database interface for Atlas 3+3 application
Provides a common interface for different database backends (SQLite, PostgreSQL)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DatabaseInterface(ABC):
    """Abstract base class for database operations"""

    @abstractmethod
    def __init__(self, config):
        """Initialize database connection"""
        pass

    @abstractmethod
    def connect(self) -> bool:
        """Establish database connection"""
        pass

    @abstractmethod
    def disconnect(self):
        """Close database connection"""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check database health and connectivity"""
        pass

    # Project operations
    @abstractmethod
    def get_all_published_projects(self) -> List[Dict[str, Any]]:
        """Get all approved/published projects"""
        pass

    @abstractmethod
    def get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed project information by ID"""
        pass

    @abstractmethod
    def get_projects_by_filters(self, region: str = None, sdg: int = None,
                               city: str = None, funded_by: str = None,
                               **kwargs) -> List[Dict[str, Any]]:
        """Filter projects by multiple criteria"""
        pass

    @abstractmethod
    def create_project(self, form_data: Dict[str, Any]) -> str:
        """Create a new project from submission form"""
        pass

    @abstractmethod
    def update_project_status(self, project_id: str, new_status: str,
                            reason: str = None, reviewer_id: str = None):
        """Update project workflow status"""
        pass

    # Admin operations
    @abstractmethod
    def get_pending_reviews(self) -> List[Dict[str, Any]]:
        """Get projects pending review"""
        pass

    @abstractmethod
    def get_admin_metrics(self) -> Dict[str, Any]:
        """Get admin dashboard metrics"""
        pass

    # Analytics operations
    @abstractmethod
    def get_kpi_metrics(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get KPI metrics for dashboard"""
        pass

    @abstractmethod
    def get_sdg_distribution(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get SDG distribution data"""
        pass

    @abstractmethod
    def get_funding_by_region(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get funding statistics by region"""
        pass

    # Reference data operations
    @abstractmethod
    def get_unique_cities(self) -> List[str]:
        """Get list of unique cities"""
        pass

    @abstractmethod
    def get_unique_organizations(self) -> List[str]:
        """Get list of unique organizations"""
        pass

    @abstractmethod
    def get_uia_regions(self) -> List[Dict[str, Any]]:
        """Get UIA regions reference data"""
        pass

    @abstractmethod
    def get_sdgs(self) -> List[Dict[str, Any]]:
        """Get SDGs reference data"""
        pass

    # Geospatial operations (optional - implemented in PostGIS version)
    def get_projects_near_location(self, latitude: float, longitude: float,
                                 radius_km: float = 50) -> List[Dict[str, Any]]:
        """Get projects within radius of location (PostGIS only)"""
        raise NotImplementedError("Geospatial operations require PostGIS")

    def get_projects_in_bounds(self, north: float, south: float,
                             east: float, west: float) -> List[Dict[str, Any]]:
        """Get projects within geographic bounds (PostGIS only)"""
        raise NotImplementedError("Geospatial operations require PostGIS")

    # Full-text search (PostgreSQL only)
    def search_projects(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Full-text search across projects (PostgreSQL only)"""
        raise NotImplementedError("Full-text search requires PostgreSQL")

    # Batch operations
    @abstractmethod
    def bulk_update_projects(self, updates: List[Dict[str, Any]]) -> int:
        """Bulk update multiple projects"""
        pass

    @abstractmethod
    def export_projects_data(self, format: str = "csv",
                           filters: Dict[str, Any] = None) -> bytes:
        """Export filtered projects data"""
        pass

class DatabaseFactory:
    """Factory class for creating database instances"""

    @staticmethod
    def create_database(config) -> DatabaseInterface:
        """Create database instance based on configuration"""
        from src.config import DatabaseType

        if config.database.db_type == DatabaseType.SQLITE:
            from src.database import AtlasDB
            return AtlasDBAdapter(config)
        elif config.database.db_type == DatabaseType.POSTGRESQL:
            from src.database_postgres import AtlasPostgreSQLDB
            return AtlasPostgreSQLDB(config)
        else:
            raise ValueError(f"Unsupported database type: {config.database.db_type}")

class AtlasDBAdapter(DatabaseInterface):
    """Adapter to make existing SQLite AtlasDB compatible with interface"""

    def __init__(self, config):
        from src.database import AtlasDB
        self.config = config
        self.db = AtlasDB(config.database.connection_string.replace("sqlite:///", ""))

    def connect(self) -> bool:
        try:
            # Test connection
            conn = self.db.get_connection()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"SQLite connection failed: {e}")
            return False

    def disconnect(self):
        # SQLite connections are managed per-operation
        pass

    def health_check(self) -> bool:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()[0]
            conn.close()
            return result == 1
        except Exception as e:
            logger.error(f"SQLite health check failed: {e}")
            return False

    # Delegate to existing SQLite implementation
    def get_all_published_projects(self) -> List[Dict[str, Any]]:
        return self.db.get_all_published_projects()

    def get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        # Convert string ID to int for SQLite
        try:
            int_id = int(project_id)
            return self.db.get_project_by_id(int_id)
        except (ValueError, TypeError):
            return None

    def get_projects_by_filters(self, region: str = None, sdg: int = None,
                               city: str = None, funded_by: str = None,
                               **kwargs) -> List[Dict[str, Any]]:
        return self.db.get_projects_by_filters(region, sdg, city, funded_by)

    def create_project(self, form_data: Dict[str, Any]) -> str:
        return self.db.create_project(form_data)

    def update_project_status(self, project_id: str, new_status: str,
                            reason: str = None, reviewer_id: str = None):
        try:
            int_id = int(project_id)
            int_reviewer_id = int(reviewer_id) if reviewer_id else None
            self.db.update_project_status(int_id, new_status, reason, int_reviewer_id)
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid project_id or reviewer_id: {e}")

    def get_pending_reviews(self) -> List[Dict[str, Any]]:
        return self.db.get_pending_reviews()

    def get_admin_metrics(self) -> Dict[str, Any]:
        return self.db.get_admin_metrics()

    def get_kpi_metrics(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        return self.db.get_kpi_metrics(filters)

    def get_sdg_distribution(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        # Simple SDG distribution for SQLite
        projects = self.get_projects_by_filters(**(filters or {}))
        sdg_counts = {}

        for project in projects:
            project_detail = self.db.get_project_by_id(project['id'])
            if project_detail and project_detail.get('sdgs'):
                for sdg in project_detail['sdgs']:
                    sdg_id = sdg['id']
                    if sdg_id not in sdg_counts:
                        sdg_counts[sdg_id] = {
                            'sdg_id': sdg_id,
                            'sdg_number': sdg_id,
                            'sdg_name': sdg['name'],
                            'sdg_color_hex': sdg['color'],
                            'project_count': 0
                        }
                    sdg_counts[sdg_id]['project_count'] += 1

        return list(sdg_counts.values())

    def get_funding_by_region(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        # Simple funding by region for SQLite
        projects = self.get_projects_by_filters(**(filters or {}))

        from src.constants import UIA_REGIONS
        region_data = {}

        for region_id, region_name in UIA_REGIONS.items():
            region_data[region_id] = {
                'region_id': region_id,
                'region_name': region_name,
                'project_count': 0,
                'total_funding_needed': 0,
                'total_funding_spent': 0
            }

        for project in projects:
            region_id = project.get('uia_region_id')
            if region_id and region_id in region_data:
                region_data[region_id]['project_count'] += 1
                funding = project.get('funding_needed_usd', 0) or 0
                region_data[region_id]['total_funding_needed'] += funding

                if project.get('project_status') == 'Implemented':
                    region_data[region_id]['total_funding_spent'] += funding

        return list(region_data.values())

    def get_unique_cities(self) -> List[str]:
        return self.db.get_unique_cities()

    def get_unique_organizations(self) -> List[str]:
        return self.db.get_unique_organizations()

    def get_uia_regions(self) -> List[Dict[str, Any]]:
        from src.constants import UIA_REGIONS
        return [
            {'region_id': rid, 'region_name': name, 'region_code': f"SECTION_{rid}"}
            for rid, name in UIA_REGIONS.items()
        ]

    def get_sdgs(self) -> List[Dict[str, Any]]:
        from src.constants import SDGS
        return [
            {
                'sdg_id': sid,
                'sdg_number': sid,
                'sdg_name': data['name'],
                'sdg_color_hex': data['color'],
                'sdg_description': data['description']
            }
            for sid, data in SDGS.items()
        ]

    def bulk_update_projects(self, updates: List[Dict[str, Any]]) -> int:
        # Simple implementation for SQLite
        count = 0
        for update in updates:
            try:
                project_id = update.get('project_id')
                new_status = update.get('workflow_status')
                reason = update.get('reason')
                reviewer_id = update.get('reviewer_id')

                if project_id and new_status:
                    self.update_project_status(project_id, new_status, reason, reviewer_id)
                    count += 1
            except Exception as e:
                logger.error(f"Failed to update project {project_id}: {e}")

        return count

    def export_projects_data(self, format: str = "csv",
                           filters: Dict[str, Any] = None) -> bytes:
        projects = self.get_projects_by_filters(**(filters or {}))

        import pandas as pd
        from src.utils import export_to_csv, export_to_xlsx

        df = pd.DataFrame(projects)

        if format.lower() == "csv":
            return export_to_csv(df)
        elif format.lower() in ["xlsx", "excel"]:
            return export_to_xlsx(df)
        else:
            raise ValueError(f"Unsupported export format: {format}")

def get_database(config=None) -> DatabaseInterface:
    """Get database instance with configuration"""
    if config is None:
        from src.config import get_config
        config = get_config()

    return DatabaseFactory.create_database(config)

# Cache for database instance
_database_instance = None

def get_cached_database() -> DatabaseInterface:
    """Get cached database instance"""
    global _database_instance
    if _database_instance is None:
        _database_instance = get_database()
    return _database_instance

def reset_database_cache():
    """Reset database cache (useful for testing)"""
    global _database_instance
    _database_instance = None