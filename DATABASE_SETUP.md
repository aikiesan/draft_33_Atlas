# Database Setup Guide - Atlas 3+3

This guide covers setting up both SQLite (development) and PostgreSQL (production) databases for the Atlas 3+3 application.

## Overview

Atlas 3+3 supports dual database backends:
- **SQLite**: For development and testing (default)
- **PostgreSQL with PostGIS**: For production with advanced geospatial features

## SQLite Setup (Development)

SQLite is the default database and requires no additional setup.

### Automatic Setup
The application automatically:
1. Creates the SQLite database file at `data/atlas_db.sqlite`
2. Initializes all required tables
3. Seeds sample data on first run

### Manual Database Reset
```bash
# Remove existing database to start fresh
rm data/atlas_db.sqlite

# Application will recreate and seed data on next run
```

## PostgreSQL Setup (Production)

### 1. Install PostgreSQL with PostGIS

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgis postgresql-postgis
```

#### CentOS/RHEL
```bash
sudo yum install postgresql postgresql-server postgresql-contrib postgis
sudo postgresql-setup initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

#### macOS (Homebrew)
```bash
brew install postgresql postgis
brew services start postgresql
```

#### Docker
```bash
docker run --name atlas-postgres \
  -e POSTGRES_DB=atlas_db \
  -e POSTGRES_USER=atlas_user \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  -d postgis/postgis:15-master
```

### 2. Create Database and User

```sql
-- Connect to PostgreSQL as superuser
sudo -u postgres psql

-- Create database and user
CREATE DATABASE atlas_db;
CREATE USER atlas_user WITH ENCRYPTED PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE atlas_db TO atlas_user;

-- Enable PostGIS extension
\c atlas_db
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Grant usage on PostGIS
GRANT USAGE ON SCHEMA topology TO atlas_user;
GRANT SELECT ON ALL TABLES IN SCHEMA topology TO atlas_user;

-- Exit
\q
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_TYPE=postgresql
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=atlas_db
DATABASE_USER=atlas_user
DATABASE_PASSWORD=your_secure_password

# SSL Configuration (optional)
DATABASE_SSL_MODE=prefer

# Connection Pool Settings
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=0
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
```

### 4. Initialize PostgreSQL Schema

The application includes comprehensive seed data with 20 sample projects from around the world.

#### Option A: Using Python Migration Tools
```python
# Run this Python script to setup schema and seed data
import sys
sys.path.append('src')

from src.config import get_config, DatabaseType
from src.database_postgres import AtlasPostgreSQLDB
from src.migrations import MigrationManager

# Override config for PostgreSQL
config = get_config()
config.database.db_type = DatabaseType.POSTGRESQL

# Initialize database with schema
db = AtlasPostgreSQLDB(config)
if db.connect():
    print("PostgreSQL database initialized successfully!")

    # Use migration tools to seed comprehensive sample data
    migration_manager = MigrationManager()
    migration_manager.setup_databases()

    if migration_manager.perform_full_migration():
        print("Sample data migration completed!")
    else:
        print("Migration failed - check logs")
else:
    print("Failed to initialize PostgreSQL database")
```

#### Option B: Direct SQL Import
```bash
# Load comprehensive seed data directly
psql -h localhost -U atlas_user -d atlas_db < POSTGRESQL_SEED_DATA.sql
```

The seed data includes:
- **5 UIA Regions** covering global geography
- **17 UN SDGs** with official colors and metadata
- **13 Project Typologies** from residential to natural environment
- **14 Requirement Types** across funding, government, and other categories
- **6 Sample Users** representing different roles (admin, reviewers, submitters)
- **20 Sample Projects** covering all 5 regions with diverse project types including:
  - Barcelona Superblocks (Urban regeneration)
  - Kigali Green City (Sustainable development)
  - Singapore Therapeutic Gardens (Health integration)
  - Medellín MetroCable (Social equity through transit)
  - Copenhagen Climate Adaptation (Blue-green infrastructure)
  - Delhi Solar Rooftop Program (Renewable energy)
  - Vancouver Zero Waste Initiative (Circular economy)
  - Tokyo Disaster Resilience (Climate adaptation)
  - And 12 additional projects from Africa, Americas, Asia, Europe, and Middle East

## Data Migration

### SQLite to PostgreSQL Migration

```python
# Run migration script
import sys
sys.path.append('src')

from src.migrations import MigrationManager

# Initialize migration manager
migration_manager = MigrationManager()

# Setup databases (will use current config)
migration_manager.setup_databases()

# Perform full migration
success = migration_manager.perform_full_migration()

if success:
    print("Migration completed successfully!")
else:
    print("Migration failed - check logs for details")
```

### Verify Migration

```python
# Verify data integrity after migration
migration_manager.verify_migration()
```

## Environment Configuration

### Development (SQLite)
```env
DATABASE_TYPE=sqlite
# No other database settings needed
```

### Production (PostgreSQL)
```env
DATABASE_TYPE=postgresql
DATABASE_HOST=your-postgres-host
DATABASE_PORT=5432
DATABASE_NAME=atlas_db
DATABASE_USER=atlas_user
DATABASE_PASSWORD=your_secure_password
DATABASE_SSL_MODE=require
```

## Database Performance

### PostgreSQL Optimization

1. **Create Indexes**
```sql
-- Geospatial indexes (created automatically by PostGIS)
-- Full-text search indexes
CREATE INDEX idx_projects_fts ON projects USING gin(to_tsvector('english', project_name || ' ' || brief_description));

-- Workflow status index
CREATE INDEX idx_projects_workflow_status ON projects(workflow_status);

-- Region index
CREATE INDEX idx_projects_region ON projects(uia_region_id);
```

2. **Materialized Views** (automatically created)
- `project_analytics_mv`: Pre-computed analytics
- `sdg_distribution_mv`: SDG distribution data
- `funding_by_region_mv`: Regional funding statistics

3. **Refresh Materialized Views**
```sql
-- Manual refresh (automated in application)
REFRESH MATERIALIZED VIEW project_analytics_mv;
REFRESH MATERIALIZED VIEW sdg_distribution_mv;
REFRESH MATERIALIZED VIEW funding_by_region_mv;
```

## Backup and Recovery

### SQLite Backup
```bash
# Simple file copy
cp data/atlas_db.sqlite data/atlas_db_backup_$(date +%Y%m%d).sqlite
```

### PostgreSQL Backup
```bash
# Full database backup
pg_dump -h localhost -U atlas_user -d atlas_db > atlas_db_backup_$(date +%Y%m%d).sql

# Restore from backup
psql -h localhost -U atlas_user -d atlas_db < atlas_db_backup_20250101.sql
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
```bash
# Fix PostgreSQL permissions
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE atlas_db TO atlas_user;"
```

2. **PostGIS Extension Missing**
```sql
-- Install PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
```

3. **Connection Issues**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check configuration
sudo -u postgres psql -c "SHOW config_file;"
```

4. **Migration Failures**
```python
# Reset migration state and retry
migration_manager.reset_migration_state()
migration_manager.perform_full_migration()
```

### Performance Issues

1. **Slow Queries**
```sql
-- Enable query logging
ALTER SYSTEM SET log_statement = 'all';
SELECT pg_reload_conf();

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM projects WHERE workflow_status = 'approved';
```

2. **Connection Pool Exhaustion**
```env
# Increase pool size in .env
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=20
```

## Security Considerations

1. **Database Access**
- Use strong passwords
- Limit database user privileges
- Enable SSL connections in production

2. **Network Security**
- Configure firewall rules
- Use VPN for database access
- Regular security updates

3. **Data Protection**
- Regular backups
- Encryption at rest
- Secure backup storage

## Monitoring

### Health Checks
```python
# Built-in health check
from src.database_interface import get_cached_database
db = get_cached_database()
health_status = db.health_check()
```

### Performance Monitoring
```sql
-- Query performance
SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;

-- Connection monitoring
SELECT count(*), state FROM pg_stat_activity GROUP BY state;
```

## Advanced Features

### Geospatial Queries (PostgreSQL only)
```python
# Find projects within 50km of location
projects = db.get_projects_near_location(
    latitude=52.3676,
    longitude=4.9041,
    radius_km=50
)

# Find projects in geographic bounds
projects = db.get_projects_in_bounds(
    north=53.0,
    south=52.0,
    east=5.0,
    west=4.0
)
```

### Full-Text Search (PostgreSQL only)
```python
# Search projects by keywords
projects = db.search_projects("renewable energy solar")
```

### Materialized Views
```python
# Get pre-computed analytics
metrics = db.get_kpi_metrics()
sdg_dist = db.get_sdg_distribution()
regional_funding = db.get_funding_by_region()
```

## Summary

Atlas 3+3 now supports both SQLite (development) and PostgreSQL (production) through a unified database interface. Key capabilities include:

### SQLite Features (Development)
- Zero-configuration setup
- Automatic sample data seeding
- All core application functionality
- Ideal for development and testing

### PostgreSQL Features (Production)
- PostGIS geospatial operations (location-based search, geographic bounds)
- Full-text search across projects
- Materialized views for high-performance analytics
- UUID primary keys and proper relational constraints
- Comprehensive seed data with 20 global sample projects
- Production-ready performance and reliability

### Migration Path
The application provides seamless migration from SQLite to PostgreSQL using built-in migration tools, enabling easy transition from development to production deployment.

All application pages (main app, dashboard, submission form, admin panel) use the same database interface, ensuring consistent functionality regardless of the backend database system.