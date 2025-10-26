"""
Configuration management for Atlas 3+3 application
Handles database connection settings and environment-based configuration
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class DatabaseType(Enum):
    """Supported database types"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"

@dataclass
class DatabaseConfig:
    """Database configuration container"""
    db_type: DatabaseType
    connection_string: str
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False

    @property
    def is_sqlite(self) -> bool:
        return self.db_type == DatabaseType.SQLITE

    @property
    def is_postgresql(self) -> bool:
        return self.db_type == DatabaseType.POSTGRESQL

class Config:
    """Application configuration manager"""

    def __init__(self):
        self._load_environment()
        self.database = self._configure_database()

    def _load_environment(self):
        """Load environment variables with defaults"""
        # Environment settings
        self.environment = os.getenv("ATLAS_ENV", "development")
        self.debug = os.getenv("ATLAS_DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("ATLAS_LOG_LEVEL", "INFO").upper()

        # Application settings
        self.app_name = os.getenv("ATLAS_APP_NAME", "Atlas 3+3")
        self.app_version = os.getenv("ATLAS_VERSION", "1.0.0")
        self.secret_key = os.getenv("ATLAS_SECRET_KEY", "dev-secret-key-change-in-production")

        # External services
        self.enable_analytics = os.getenv("ATLAS_ENABLE_ANALYTICS", "false").lower() == "true"
        self.enable_caching = os.getenv("ATLAS_ENABLE_CACHING", "true").lower() == "true"

    def _configure_database(self) -> DatabaseConfig:
        """Configure database based on environment"""
        db_type_str = os.getenv("ATLAS_DB_TYPE", "sqlite").lower()

        try:
            db_type = DatabaseType(db_type_str)
        except ValueError:
            logger.warning(f"Invalid database type '{db_type_str}', defaulting to SQLite")
            db_type = DatabaseType.SQLITE

        if db_type == DatabaseType.SQLITE:
            return self._configure_sqlite()
        elif db_type == DatabaseType.POSTGRESQL:
            return self._configure_postgresql()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def _configure_sqlite(self) -> DatabaseConfig:
        """Configure SQLite database"""
        db_path = os.getenv("ATLAS_SQLITE_PATH", "data/atlas_db.sqlite")

        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)

        connection_string = f"sqlite:///{db_path}"

        return DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            connection_string=connection_string,
            echo=self.debug
        )

    def _configure_postgresql(self) -> DatabaseConfig:
        """Configure PostgreSQL database"""
        # Database connection parameters
        host = os.getenv("ATLAS_DB_HOST", "localhost")
        port = int(os.getenv("ATLAS_DB_PORT", "5432"))
        database = os.getenv("ATLAS_DB_NAME", "atlas_3_3")
        username = os.getenv("ATLAS_DB_USER", "atlas_user")
        password = os.getenv("ATLAS_DB_PASSWORD")

        if not password:
            if self.environment == "production":
                raise ValueError("Database password is required for production environment")
            else:
                logger.warning("No database password provided, using default for development")
                password = "atlas_dev_password"

        # Connection pool settings
        pool_size = int(os.getenv("ATLAS_DB_POOL_SIZE", "5"))
        max_overflow = int(os.getenv("ATLAS_DB_MAX_OVERFLOW", "10"))

        # Build connection string
        connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"

        return DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            connection_string=connection_string,
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=self.debug
        )

    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() in ["development", "dev", "local"]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() in ["production", "prod"]

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.environment.lower() in ["testing", "test"]

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                },
                "detailed": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
                }
            },
            "handlers": {
                "default": {
                    "level": self.log_level,
                    "formatter": "detailed" if self.debug else "standard",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout"
                }
            },
            "loggers": {
                "": {
                    "handlers": ["default"],
                    "level": self.log_level,
                    "propagate": False
                },
                "sqlalchemy.engine": {
                    "handlers": ["default"],
                    "level": "INFO" if self.debug else "WARNING",
                    "propagate": False
                }
            }
        }

    def validate_config(self) -> bool:
        """Validate configuration settings"""
        errors = []

        # Validate database configuration
        if self.database.is_postgresql:
            if not self.database.host:
                errors.append("PostgreSQL host is required")
            if not self.database.database:
                errors.append("PostgreSQL database name is required")
            if not self.database.username:
                errors.append("PostgreSQL username is required")
            if not self.database.password:
                errors.append("PostgreSQL password is required")

        # Validate production-specific settings
        if self.is_production:
            if self.secret_key == "dev-secret-key-change-in-production":
                errors.append("Secret key must be changed for production")
            if self.debug:
                errors.append("Debug mode should be disabled in production")

        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            return False

        return True

    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary (without sensitive data)"""
        summary = {
            "environment": self.environment,
            "debug": self.debug,
            "app_name": self.app_name,
            "app_version": self.app_version,
            "database_type": self.database.db_type.value,
            "log_level": self.log_level,
            "enable_analytics": self.enable_analytics,
            "enable_caching": self.enable_caching
        }

        if self.database.is_postgresql:
            summary.update({
                "db_host": self.database.host,
                "db_port": self.database.port,
                "db_name": self.database.database,
                "db_username": self.database.username,
                "db_pool_size": self.database.pool_size
            })
        elif self.database.is_sqlite:
            summary["db_path"] = self.database.connection_string.replace("sqlite:///", "")

        return summary

# Global configuration instance
config = Config()

def get_config() -> Config:
    """Get the global configuration instance"""
    return config

def reload_config() -> Config:
    """Reload configuration from environment"""
    global config
    config = Config()
    return config

# Environment variable documentation
ENV_DOCS = {
    # Core settings
    "ATLAS_ENV": "Environment name (development, testing, production)",
    "ATLAS_DEBUG": "Enable debug mode (true/false)",
    "ATLAS_LOG_LEVEL": "Logging level (DEBUG, INFO, WARNING, ERROR)",
    "ATLAS_SECRET_KEY": "Secret key for sessions and security",

    # Database settings
    "ATLAS_DB_TYPE": "Database type (sqlite, postgresql)",
    "ATLAS_SQLITE_PATH": "SQLite database file path",
    "ATLAS_DB_HOST": "PostgreSQL host",
    "ATLAS_DB_PORT": "PostgreSQL port",
    "ATLAS_DB_NAME": "PostgreSQL database name",
    "ATLAS_DB_USER": "PostgreSQL username",
    "ATLAS_DB_PASSWORD": "PostgreSQL password",
    "ATLAS_DB_POOL_SIZE": "Database connection pool size",
    "ATLAS_DB_MAX_OVERFLOW": "Database connection pool overflow",

    # Feature flags
    "ATLAS_ENABLE_ANALYTICS": "Enable analytics tracking (true/false)",
    "ATLAS_ENABLE_CACHING": "Enable caching (true/false)",

    # Application info
    "ATLAS_APP_NAME": "Application name",
    "ATLAS_VERSION": "Application version"
}

def print_env_docs():
    """Print environment variable documentation"""
    print("Atlas 3+3 Environment Variables:")
    print("=" * 50)
    for var, description in ENV_DOCS.items():
        print(f"{var:<25} - {description}")

if __name__ == "__main__":
    # Configuration testing and documentation
    import json

    config = get_config()

    print("Atlas 3+3 Configuration")
    print("=" * 30)
    print(json.dumps(config.get_summary(), indent=2))
    print()

    if config.validate_config():
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration has errors")

    print()
    print_env_docs()