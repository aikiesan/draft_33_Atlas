import sqlite3
import pandas as pd
from datetime import datetime
import json
import os
from typing import Optional, List, Dict, Any

class AtlasDB:
    def __init__(self, db_path="data/atlas_db.sqlite"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        self.init_db()
        if self.is_empty_db():
            self.seed_sample_data()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Create all tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create UIA Regions reference table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS uia_regions (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
        ''')

        # Create SDGs reference table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sdgs (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            color TEXT NOT NULL,
            description TEXT
        )
        ''')

        # Create Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            organization_name TEXT,
            contact_person TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin BOOLEAN DEFAULT FALSE
        )
        ''')

        # Create Projects table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            funding_needed_usd DECIMAL(15,2),
            uia_region_id INTEGER REFERENCES uia_regions(id),
            city TEXT,
            country TEXT,
            latitude DECIMAL(10,8),
            longitude DECIMAL(11,8),
            organization_name TEXT,
            contact_person TEXT,
            contact_email TEXT,
            brief_description TEXT,
            detailed_description TEXT,
            success_factors TEXT,
            project_status TEXT CHECK (project_status IN ('Planned', 'In Progress', 'Implemented')),
            workflow_status TEXT DEFAULT 'submitted' CHECK (workflow_status IN ('submitted', 'in_review', 'approved', 'rejected', 'changes_requested')),
            reference_id TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            submitted_by INTEGER REFERENCES users(id)
        )
        ''')

        # Create Project SDGs junction table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_sdgs (
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            sdg_id INTEGER REFERENCES sdgs(id),
            PRIMARY KEY (project_id, sdg_id)
        )
        ''')

        # Create Project Typologies table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_typologies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            typology TEXT NOT NULL,
            other_description TEXT
        )
        ''')

        # Create Project Requirements table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            requirement_category TEXT NOT NULL,
            requirement_text TEXT NOT NULL,
            other_description TEXT
        )
        ''')

        # Create Project Images table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            image_url TEXT NOT NULL,
            alt_text TEXT,
            is_primary BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create Project Workflow History table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_workflow_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            old_status TEXT,
            new_status TEXT,
            changed_by INTEGER REFERENCES users(id),
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create Reviews table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            reviewer_id INTEGER REFERENCES users(id),
            review_status TEXT CHECK (review_status IN ('approved', 'rejected', 'changes_requested')),
            notes TEXT,
            content_accurate BOOLEAN,
            images_appropriate BOOLEAN,
            no_spam BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.commit()
        conn.close()

        # Populate reference data
        self.populate_reference_data()

    def populate_reference_data(self):
        """Populate UIA regions and SDGs reference data"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # UIA Regions
        regions = [
            (1, "Section I - Western Europe", "Western European countries"),
            (2, "Section II - Middle East and Eastern Europe", "Middle East and Eastern European countries"),
            (3, "Section III - Americas", "North, Central and South American countries"),
            (4, "Section IV - Oceania", "Oceanic countries and territories"),
            (5, "Section V - Africa", "African countries")
        ]

        cursor.executemany('''
        INSERT OR IGNORE INTO uia_regions (id, name, description) VALUES (?, ?, ?)
        ''', regions)

        # SDGs with official colors
        sdgs = [
            (1, "No Poverty", "#E5243B", "End poverty in all its forms everywhere"),
            (2, "Zero Hunger", "#DDA63A", "End hunger, achieve food security and improved nutrition"),
            (3, "Good Health and Well-being", "#4C9F38", "Ensure healthy lives and promote well-being for all"),
            (4, "Quality Education", "#C5192D", "Ensure inclusive and equitable quality education"),
            (5, "Gender Equality", "#FF3A21", "Achieve gender equality and empower all women and girls"),
            (6, "Clean Water and Sanitation", "#26BDE2", "Ensure availability and sustainable management of water"),
            (7, "Affordable and Clean Energy", "#FCC30B", "Ensure access to affordable, reliable, sustainable energy"),
            (8, "Decent Work and Economic Growth", "#A21942", "Promote sustained, inclusive economic growth"),
            (9, "Industry, Innovation and Infrastructure", "#FD6925", "Build resilient infrastructure, promote innovation"),
            (10, "Reduced Inequalities", "#DD1367", "Reduce inequality within and among countries"),
            (11, "Sustainable Cities and Communities", "#FD9D24", "Make cities and human settlements sustainable"),
            (12, "Responsible Consumption and Production", "#BF8B2E", "Ensure sustainable consumption and production patterns"),
            (13, "Climate Action", "#3F7E44", "Take urgent action to combat climate change"),
            (14, "Life Below Water", "#0A97D9", "Conserve and sustainably use the oceans, seas"),
            (15, "Life on Land", "#56C02B", "Protect, restore and promote sustainable use of ecosystems"),
            (16, "Peace, Justice and Strong Institutions", "#00689D", "Promote peaceful and inclusive societies"),
            (17, "Partnerships for the Goals", "#19486A", "Strengthen means of implementation and partnerships")
        ]

        cursor.executemany('''
        INSERT OR IGNORE INTO sdgs (id, name, color, description) VALUES (?, ?, ?, ?)
        ''', sdgs)

        conn.commit()
        conn.close()

    def is_empty_db(self):
        """Check if database has any projects"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM projects")
        count = cursor.fetchone()[0]
        conn.close()
        return count == 0

    def seed_sample_data(self):
        """Insert sample projects on first run"""
        sample_projects = [
            {
                "project_name": "Urban Green Corridor Initiative",
                "funding_needed_usd": 2500000,
                "uia_region_id": 1,
                "city": "Amsterdam",
                "country": "Netherlands",
                "latitude": 52.3676,
                "longitude": 4.9041,
                "organization_name": "Amsterdam Urban Planning Department",
                "contact_person": "Maria van den Berg",
                "contact_email": "maria.vandenberg@amsterdam.nl",
                "brief_description": "Creating interconnected green spaces throughout the city center",
                "detailed_description": "A comprehensive urban planning initiative to create connected green corridors that improve air quality, provide recreational spaces, and support biodiversity in the city center.",
                "success_factors": "Strong municipal support, community engagement, and integrated approach to urban planning",
                "project_status": "In Progress",
                "workflow_status": "approved",
                "sdgs": [11, 13, 15],
                "typologies": ["Public Realm & Urban Landscape", "Natural Environment & Ecological Projects"],
                "requirements": [
                    ("Government & Regulatory", "Local / Municipal Support & Endorsement"),
                    ("Funding & Financial", "Public Funding / Government Grants"),
                    ("Other", "Availability of Land / Site")
                ],
                "images": ["https://via.placeholder.com/800x400/4C9F38/ffffff?text=Green+Corridor"]
            },
            {
                "project_name": "Smart Healthcare Hub",
                "funding_needed_usd": 5200000,
                "uia_region_id": 3,
                "city": "São Paulo",
                "country": "Brazil",
                "latitude": -23.5505,
                "longitude": -46.6333,
                "organization_name": "São Paulo Health Innovation Center",
                "contact_person": "Dr. Carlos Santos",
                "contact_email": "carlos.santos@sphic.org.br",
                "brief_description": "Digital healthcare facility with telemedicine and AI diagnostic capabilities",
                "detailed_description": "A state-of-the-art healthcare facility integrating telemedicine, AI-powered diagnostics, and community health programs to improve healthcare access in underserved areas.",
                "success_factors": "Technology integration, community trust, and sustainable financing model",
                "project_status": "Planned",
                "workflow_status": "approved",
                "sdgs": [3, 9, 10],
                "typologies": ["Healthcare", "Infrastructure & Utilities"],
                "requirements": [
                    ("Funding & Financial", "Private Investment / Corporate Sponsorship"),
                    ("Government & Regulatory", "Regional / Gubernatorial Support"),
                    ("Other", "Strong Project Leadership & Management")
                ],
                "images": ["https://via.placeholder.com/800x400/4C9F38/ffffff?text=Smart+Healthcare"]
            },
            {
                "project_name": "Sustainable Water Management System",
                "funding_needed_usd": 3800000,
                "uia_region_id": 5,
                "city": "Cape Town",
                "country": "South Africa",
                "latitude": -33.9249,
                "longitude": 18.4241,
                "organization_name": "Cape Town Water Department",
                "contact_person": "Nomsa Mbeki",
                "contact_email": "nomsa.mbeki@capetown.gov.za",
                "brief_description": "Integrated water recycling and rainwater harvesting infrastructure",
                "detailed_description": "Comprehensive water management system combining greywater recycling, rainwater harvesting, and smart distribution networks to ensure water security.",
                "success_factors": "Community participation, advanced technology adoption, and climate resilience planning",
                "project_status": "Implemented",
                "workflow_status": "approved",
                "sdgs": [6, 11, 13],
                "typologies": ["Infrastructure & Utilities", "Natural Environment & Ecological Projects"],
                "requirements": [
                    ("Government & Regulatory", "National Government Support & Political Will"),
                    ("Funding & Financial", "International Aid / Development Grants"),
                    ("Other", "Media Coverage & Public Awareness")
                ],
                "images": ["https://via.placeholder.com/800x400/26BDE2/ffffff?text=Water+Management"]
            },
            {
                "project_name": "Digital Education Platform",
                "funding_needed_usd": 1200000,
                "uia_region_id": 4,
                "city": "Sydney",
                "country": "Australia",
                "latitude": -33.8688,
                "longitude": 151.2093,
                "organization_name": "Sydney Educational Technology Institute",
                "contact_person": "Jennifer Williams",
                "contact_email": "j.williams@seti.edu.au",
                "brief_description": "AI-powered personalized learning platform for disadvantaged communities",
                "detailed_description": "An innovative digital education platform that uses AI to provide personalized learning experiences, connecting students in remote areas with quality educational resources.",
                "success_factors": "Digital literacy programs, reliable internet infrastructure, and teacher training initiatives",
                "project_status": "In Progress",
                "workflow_status": "approved",
                "sdgs": [4, 9, 10],
                "typologies": ["Educational", "Infrastructure & Utilities"],
                "requirements": [
                    ("Funding & Financial", "Philanthropic Support"),
                    ("Government & Regulatory", "Favorable Policies or Regulations"),
                    ("Other", "Strong Project Leadership & Management")
                ],
                "images": ["https://via.placeholder.com/800x400/C5192D/ffffff?text=Digital+Education"]
            },
            {
                "project_name": "Renewable Energy Cooperative",
                "funding_needed_usd": 4500000,
                "uia_region_id": 2,
                "city": "Istanbul",
                "country": "Turkey",
                "latitude": 41.0082,
                "longitude": 28.9784,
                "organization_name": "Istanbul Energy Cooperative",
                "contact_person": "Ahmet Özkan",
                "contact_email": "ahmet.ozkan@istanbulenerji.org",
                "brief_description": "Community-owned solar and wind energy generation network",
                "detailed_description": "A cooperative model for renewable energy generation where community members own shares in solar and wind installations, promoting energy independence and sustainability.",
                "success_factors": "Community ownership model, favorable energy policies, and technical expertise availability",
                "project_status": "Planned",
                "workflow_status": "approved",
                "sdgs": [7, 11, 13],
                "typologies": ["Infrastructure & Utilities", "Natural Environment & Ecological Projects"],
                "requirements": [
                    ("Government & Regulatory", "Favorable Policies or Regulations"),
                    ("Funding & Financial", "Community Funding / Crowdfunding"),
                    ("Other", "Availability of Land / Site")
                ],
                "images": ["https://via.placeholder.com/800x400/FCC30B/000000?text=Renewable+Energy"]
            }
        ]

        conn = self.get_connection()
        cursor = conn.cursor()

        # Create admin user
        cursor.execute('''
        INSERT OR IGNORE INTO users (email, organization_name, contact_person, is_admin)
        VALUES (?, ?, ?, ?)
        ''', ("admin@atlas33.org", "Atlas 3+3 Team", "Admin User", True))

        admin_user_id = cursor.lastrowid or 1

        for i, project_data in enumerate(sample_projects, 1):
            # Generate reference ID
            ref_id = f"ATLAS-2025-{str(i).zfill(6)}"

            # Insert project
            cursor.execute('''
            INSERT INTO projects (
                project_name, funding_needed_usd, uia_region_id, city, country,
                latitude, longitude, organization_name, contact_person, contact_email,
                brief_description, detailed_description, success_factors,
                project_status, workflow_status, reference_id, submitted_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project_data["project_name"], project_data["funding_needed_usd"],
                project_data["uia_region_id"], project_data["city"], project_data["country"],
                project_data["latitude"], project_data["longitude"],
                project_data["organization_name"], project_data["contact_person"],
                project_data["contact_email"], project_data["brief_description"],
                project_data["detailed_description"], project_data["success_factors"],
                project_data["project_status"], project_data["workflow_status"],
                ref_id, admin_user_id
            ))

            project_id = cursor.lastrowid

            # Insert SDGs
            for sdg_id in project_data["sdgs"]:
                cursor.execute('''
                INSERT INTO project_sdgs (project_id, sdg_id) VALUES (?, ?)
                ''', (project_id, sdg_id))

            # Insert typologies
            for typology in project_data["typologies"]:
                cursor.execute('''
                INSERT INTO project_typologies (project_id, typology) VALUES (?, ?)
                ''', (project_id, typology))

            # Insert requirements
            for category, requirement in project_data["requirements"]:
                cursor.execute('''
                INSERT INTO project_requirements (project_id, requirement_category, requirement_text)
                VALUES (?, ?, ?)
                ''', (project_id, category, requirement))

            # Insert images
            for image_url in project_data["images"]:
                cursor.execute('''
                INSERT INTO project_images (project_id, image_url, is_primary)
                VALUES (?, ?, ?)
                ''', (project_id, image_url, True))

        conn.commit()
        conn.close()

    def get_all_published_projects(self) -> List[Dict[str, Any]]:
        """Returns all approved projects"""
        conn = self.get_connection()
        query = '''
        SELECT p.*, ur.name as region_name
        FROM projects p
        LEFT JOIN uia_regions ur ON p.uia_region_id = ur.id
        WHERE p.workflow_status = 'approved'
        ORDER BY p.created_at DESC
        '''
        df = pd.read_sql(query, conn)
        conn.close()
        return df.to_dict('records')

    def get_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed project information by ID"""
        conn = self.get_connection()

        # Get basic project info
        cursor = conn.cursor()
        cursor.execute('''
        SELECT p.*, ur.name as region_name
        FROM projects p
        LEFT JOIN uia_regions ur ON p.uia_region_id = ur.id
        WHERE p.id = ?
        ''', (project_id,))

        project = cursor.fetchone()
        if not project:
            conn.close()
            return None

        project = dict(project)

        # Get SDGs
        cursor.execute('''
        SELECT s.id, s.name, s.color
        FROM project_sdgs ps
        JOIN sdgs s ON ps.sdg_id = s.id
        WHERE ps.project_id = ?
        ''', (project_id,))
        project['sdgs'] = [dict(row) for row in cursor.fetchall()]

        # Get typologies
        cursor.execute('''
        SELECT typology, other_description
        FROM project_typologies
        WHERE project_id = ?
        ''', (project_id,))
        project['typologies'] = [dict(row) for row in cursor.fetchall()]

        # Get requirements
        cursor.execute('''
        SELECT requirement_category, requirement_text, other_description
        FROM project_requirements
        WHERE project_id = ?
        ''', (project_id,))
        project['requirements'] = [dict(row) for row in cursor.fetchall()]

        # Get images
        cursor.execute('''
        SELECT image_url, alt_text, is_primary
        FROM project_images
        WHERE project_id = ?
        ORDER BY is_primary DESC, created_at ASC
        ''', (project_id,))
        project['images'] = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return project

    def get_projects_by_filters(self, region=None, sdg=None, city=None, funded_by=None) -> List[Dict[str, Any]]:
        """Filter projects by multiple criteria"""
        conn = self.get_connection()

        query = '''
        SELECT DISTINCT p.*, ur.name as region_name
        FROM projects p
        LEFT JOIN uia_regions ur ON p.uia_region_id = ur.id
        LEFT JOIN project_sdgs ps ON p.id = ps.project_id
        WHERE p.workflow_status = 'approved'
        '''

        params = []

        if region:
            query += ' AND ur.name = ?'
            params.append(region)

        if sdg:
            query += ' AND ps.sdg_id = ?'
            params.append(sdg)

        if city:
            query += ' AND LOWER(p.city) = LOWER(?)'
            params.append(city)

        if funded_by:
            query += ' AND LOWER(p.organization_name) LIKE LOWER(?)'
            params.append(f'%{funded_by}%')

        query += ' ORDER BY p.created_at DESC'

        df = pd.read_sql(query, conn, params=params)
        conn.close()
        return df.to_dict('records')

    def get_kpi_metrics(self, filters=None) -> Dict[str, Any]:
        """Returns KPI data: total projects, cities, countries, funding"""
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
            'funding_needed': df['funding_needed_usd'].sum(),
            'funding_spent': df[df['project_status'] == 'Implemented']['funding_needed_usd'].sum()
        }

    def get_unique_cities(self) -> List[str]:
        """Get list of unique cities"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT DISTINCT city FROM projects
        WHERE workflow_status = 'approved' AND city IS NOT NULL
        ORDER BY city
        ''')
        cities = [row[0] for row in cursor.fetchall()]
        conn.close()
        return cities

    def get_unique_organizations(self) -> List[str]:
        """Get list of unique organizations"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT DISTINCT organization_name FROM projects
        WHERE workflow_status = 'approved' AND organization_name IS NOT NULL
        ORDER BY organization_name
        ''')
        orgs = [row[0] for row in cursor.fetchall()]
        conn.close()
        return orgs

    def create_project(self, form_data: Dict[str, Any]) -> str:
        """Inserts new project from submission form"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Generate reference ID
        cursor.execute("SELECT COUNT(*) FROM projects")
        count = cursor.fetchone()[0]
        ref_id = f"ATLAS-2025-{str(count + 1).zfill(6)}"

        # Create or get user
        cursor.execute('''
        INSERT OR IGNORE INTO users (email, organization_name, contact_person)
        VALUES (?, ?, ?)
        ''', (form_data['contact_email'], form_data['organization_name'], form_data['contact_person']))

        cursor.execute('SELECT id FROM users WHERE email = ?', (form_data['contact_email'],))
        user_id = cursor.fetchone()[0]

        # Insert project
        cursor.execute('''
        INSERT INTO projects (
            project_name, funding_needed_usd, uia_region_id, city, country,
            latitude, longitude, organization_name, contact_person, contact_email,
            brief_description, detailed_description, success_factors,
            project_status, workflow_status, reference_id, submitted_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            form_data['project_name'], form_data.get('funding_needed_usd'),
            form_data['uia_region_id'], form_data['city'], form_data['country'],
            form_data.get('latitude'), form_data.get('longitude'),
            form_data['organization_name'], form_data['contact_person'],
            form_data['contact_email'], form_data['brief_description'],
            form_data['detailed_description'], form_data['success_factors'],
            form_data['project_status'], 'submitted', ref_id, user_id
        ))

        project_id = cursor.lastrowid

        # Insert SDGs
        for sdg_id in form_data.get('sdgs', []):
            cursor.execute('INSERT INTO project_sdgs (project_id, sdg_id) VALUES (?, ?)',
                         (project_id, sdg_id))

        # Insert typologies
        for typology in form_data.get('typologies', []):
            cursor.execute('INSERT INTO project_typologies (project_id, typology) VALUES (?, ?)',
                         (project_id, typology))

        # Insert requirements
        for req in form_data.get('requirements', []):
            cursor.execute('''
            INSERT INTO project_requirements (project_id, requirement_category, requirement_text)
            VALUES (?, ?, ?)
            ''', (project_id, req['category'], req['text']))

        # Insert images
        for image_url in form_data.get('image_urls', []):
            if image_url.strip():
                cursor.execute('''
                INSERT INTO project_images (project_id, image_url, is_primary)
                VALUES (?, ?, ?)
                ''', (project_id, image_url.strip(), False))

        conn.commit()
        conn.close()
        return ref_id

    def update_project_status(self, project_id: int, new_status: str, reason: str = None, reviewer_id: int = None):
        """Updates workflow status (for approvals/rejections)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get current status
        cursor.execute('SELECT workflow_status FROM projects WHERE id = ?', (project_id,))
        old_status = cursor.fetchone()[0]

        # Update project status
        cursor.execute('''
        UPDATE projects
        SET workflow_status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (new_status, project_id))

        # Insert workflow history
        cursor.execute('''
        INSERT INTO project_workflow_history
        (project_id, old_status, new_status, changed_by, reason)
        VALUES (?, ?, ?, ?, ?)
        ''', (project_id, old_status, new_status, reviewer_id, reason))

        # Insert review record if reviewer provided
        if reviewer_id:
            cursor.execute('''
            INSERT INTO reviews (project_id, reviewer_id, review_status, notes)
            VALUES (?, ?, ?, ?)
            ''', (project_id, reviewer_id, new_status, reason))

        conn.commit()
        conn.close()

    def get_pending_reviews(self) -> List[Dict[str, Any]]:
        """Get projects pending review"""
        conn = self.get_connection()
        query = '''
        SELECT p.*, ur.name as region_name
        FROM projects p
        LEFT JOIN uia_regions ur ON p.uia_region_id = ur.id
        WHERE p.workflow_status IN ('submitted', 'in_review', 'changes_requested')
        ORDER BY p.created_at ASC
        '''
        df = pd.read_sql(query, conn)
        conn.close()
        return df.to_dict('records')

    def get_admin_metrics(self) -> Dict[str, Any]:
        """Get admin dashboard metrics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Pending reviews
        cursor.execute("SELECT COUNT(*) FROM projects WHERE workflow_status IN ('submitted', 'in_review')")
        pending = cursor.fetchone()[0]

        # This month's approvals
        cursor.execute('''
        SELECT COUNT(*) FROM projects
        WHERE workflow_status = 'approved'
        AND date(updated_at) >= date('now', 'start of month')
        ''')
        approved_month = cursor.fetchone()[0]

        # This month's rejections
        cursor.execute('''
        SELECT COUNT(*) FROM projects
        WHERE workflow_status = 'rejected'
        AND date(updated_at) >= date('now', 'start of month')
        ''')
        rejected_month = cursor.fetchone()[0]

        # Total published
        cursor.execute("SELECT COUNT(*) FROM projects WHERE workflow_status = 'approved'")
        total_published = cursor.fetchone()[0]

        conn.close()

        return {
            'pending_reviews': pending,
            'approved_this_month': approved_month,
            'rejected_this_month': rejected_month,
            'total_published': total_published,
            'avg_review_time': "2.3 days"  # Placeholder
        }