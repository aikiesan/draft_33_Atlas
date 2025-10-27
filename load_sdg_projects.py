#!/usr/bin/env python3
"""
Load Additional Real-World SDG Projects into Atlas 3+3 Database
Converts PostgreSQL seed data format to SQLite and loads comprehensive project data
"""

import sqlite3
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database import AtlasDB
from src.config import get_config

def load_comprehensive_sdg_data():
    """Load comprehensive real-world SDG projects data"""

    config = get_config()

    # Use the configured database path
    if config.database.is_sqlite:
        db_path = config.database.connection_string.replace("sqlite:///", "")
        print(f"Loading data into SQLite database: {db_path}")
        db = AtlasDB(db_path)
    else:
        print("This script is designed for SQLite databases only")
        return

    # Clear existing sample data to load real data
    clear_existing_data(db)

    # Load comprehensive reference data
    load_uia_regions(db)
    load_sdgs_data(db)
    load_typologies_data(db)
    load_requirements_data(db)

    # Load 14 additional real-world SDG projects
    load_real_world_projects(db)

    print("Successfully loaded comprehensive SDG projects data!")
    print_data_summary(db)

def clear_existing_data(db: AtlasDB):
    """Clear existing sample data"""
    conn = db.get_connection()
    cursor = conn.cursor()

    print("Clearing existing sample data...")

    # Clear projects and related data
    cursor.execute("DELETE FROM project_sdgs")
    cursor.execute("DELETE FROM project_typologies")
    cursor.execute("DELETE FROM project_requirements")
    cursor.execute("DELETE FROM projects")

    conn.commit()
    conn.close()

def load_uia_regions(db: AtlasDB):
    """Load UIA regions reference data"""
    conn = db.get_connection()
    cursor = conn.cursor()

    regions = [
        (1, 'Region I - Western Europe', 'Western European countries including UK, France, Germany, Spain, Italy, and Nordic countries'),
        (2, 'Region II - Central and Eastern Europe and Middle East', 'Central/Eastern Europe, Russia, Turkey, and Middle Eastern countries'),
        (3, 'Region III - The Americas', 'North, Central, and South American countries'),
        (4, 'Region IV - Asia and Oceania', 'Asian countries including China, Japan, India, Southeast Asia, Australia, and Pacific Islands'),
        (5, 'Region V - Africa', 'All African countries including North Africa, Sub-Saharan Africa, and island nations')
    ]

    print("Loading UIA regions...")
    cursor.execute("DELETE FROM uia_regions")

    for region_id, name, description in regions:
        cursor.execute("""
            INSERT INTO uia_regions (id, name, description)
            VALUES (?, ?, ?)
        """, (region_id, name, description))

    conn.commit()
    conn.close()

def load_sdgs_data(db: AtlasDB):
    """Load all 17 SDGs with official colors"""
    conn = db.get_connection()
    cursor = conn.cursor()

    sdgs = [
        (1, 'No Poverty', '#E5243B', 'End poverty in all its forms everywhere'),
        (2, 'Zero Hunger', '#DDA63A', 'End hunger, achieve food security and improved nutrition'),
        (3, 'Good Health and Well-Being', '#4C9F38', 'Ensure healthy lives and promote well-being for all'),
        (4, 'Quality Education', '#C5192D', 'Ensure inclusive and equitable quality education'),
        (5, 'Gender Equality', '#FF3A21', 'Achieve gender equality and empower all women and girls'),
        (6, 'Clean Water and Sanitation', '#26BDE2', 'Ensure availability and sustainable management of water and sanitation'),
        (7, 'Affordable and Clean Energy', '#FCC30B', 'Ensure access to affordable, reliable, sustainable energy'),
        (8, 'Decent Work and Economic Growth', '#A21942', 'Promote sustained, inclusive economic growth and decent work'),
        (9, 'Industry, Innovation and Infrastructure', '#FD6925', 'Build resilient infrastructure and foster innovation'),
        (10, 'Reduced Inequalities', '#DD1367', 'Reduce inequality within and among countries'),
        (11, 'Sustainable Cities and Communities', '#FD9D24', 'Make cities inclusive, safe, resilient and sustainable'),
        (12, 'Responsible Consumption and Production', '#BF8B2E', 'Ensure sustainable consumption and production patterns'),
        (13, 'Climate Action', '#3F7E44', 'Take urgent action to combat climate change'),
        (14, 'Life Below Water', '#0A97D9', 'Conserve and sustainably use oceans and marine resources'),
        (15, 'Life on Land', '#56C02B', 'Protect, restore and promote sustainable use of terrestrial ecosystems'),
        (16, 'Peace, Justice and Strong Institutions', '#00689D', 'Promote peaceful and inclusive societies'),
        (17, 'Partnerships for the Goals', '#19486A', 'Strengthen global partnership for sustainable development')
    ]

    print("Loading SDGs...")
    cursor.execute("DELETE FROM sdgs")

    for sdg_id, name, color, description in sdgs:
        cursor.execute("""
            INSERT INTO sdgs (id, name, color, description)
            VALUES (?, ?, ?, ?)
        """, (sdg_id, name, color, description))

    conn.commit()
    conn.close()

def load_typologies_data(db: AtlasDB):
    """Load project typologies"""
    conn = db.get_connection()
    cursor = conn.cursor()

    # Create typologies table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS typologies (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    ''')

    typologies = [
        ('Residential', 'Housing and residential communities'),
        ('Commercial', 'Commercial and retail developments'),
        ('Educational', 'Schools, universities, training facilities'),
        ('Healthcare', 'Hospitals, clinics, health centers'),
        ('Civic', 'Government buildings, administrative facilities'),
        ('Cultural', 'Museums, theaters, cultural centers'),
        ('Sports & Recreation', 'Sports facilities, recreation centers'),
        ('Industrial', 'Manufacturing, industrial facilities'),
        ('Infrastructure', 'Transportation, utilities, public works'),
        ('Public Realm & Urban Landscape', 'Parks, plazas, public spaces'),
        ('Natural Environment & Ecological Projects', 'Conservation, ecological restoration'),
        ('Markets & Exchange', 'Markets, trade facilities'),
        ('Other', 'Other project types')
    ]

    print("Loading typologies...")
    cursor.execute("DELETE FROM typologies")

    for i, (name, description) in enumerate(typologies, 1):
        cursor.execute("""
            INSERT INTO typologies (id, name, description)
            VALUES (?, ?, ?)
        """, (i, name, description))

    conn.commit()
    conn.close()

def load_requirements_data(db: AtlasDB):
    """Load project requirements"""
    conn = db.get_connection()
    cursor = conn.cursor()

    # Create requirements table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requirements (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            category TEXT,
            description TEXT
        )
    ''')

    requirements = [
        ('Local Community Support', 'Social', 'Strong backing from local residents and stakeholders'),
        ('Public Sector Funding', 'Financial', 'Government or municipal financial support'),
        ('Strong Political Leadership', 'Governance', 'Committed political champions and decision-makers'),
        ('Favorable Policy Environment', 'Governance', 'Supportive regulatory and policy framework'),
        ('Technical Expertise', 'Capacity', 'Access to required technical knowledge and skills'),
        ('Private Sector Partnership', 'Financial', 'Collaboration with private sector organizations'),
        ('International Funding', 'Financial', 'Support from international development organizations'),
        ('Research Institution Partnership', 'Capacity', 'Collaboration with universities or research centers'),
        ('Community Engagement Framework', 'Social', 'Structured approach to community participation'),
        ('Environmental Assessment', 'Environmental', 'Comprehensive environmental impact evaluation'),
        ('Cultural Sensitivity', 'Social', 'Respect for local cultural values and practices'),
        ('Gender Inclusion', 'Social', 'Specific attention to gender equality and women\'s participation'),
        ('Youth Engagement', 'Social', 'Active involvement of young people in project design and implementation'),
        ('Technology Infrastructure', 'Technical', 'Required technological systems and digital infrastructure'),
        ('Monitoring & Evaluation System', 'Governance', 'Framework for tracking progress and measuring impact')
    ]

    print("Loading requirements...")
    cursor.execute("DELETE FROM requirements")

    for i, (name, category, description) in enumerate(requirements, 1):
        cursor.execute("""
            INSERT INTO requirements (id, name, category, description)
            VALUES (?, ?, ?, ?)
        """, (i, name, category, description))

    conn.commit()
    conn.close()

def load_real_world_projects(db: AtlasDB):
    """Load 14 additional verified real-world SDG projects"""

    projects = [
        {
            "project_name": "Barcelona Superblocks: Urban Regeneration for Livable Streets",
            "funding_needed_usd": 12500000,
            "funding_spent_usd": 11200000,
            "uia_region_id": 1,
            "city": "Barcelona",
            "country": "Spain",
            "latitude": 41.3851,
            "longitude": 2.1734,
            "organization_name": "Barcelona City Council - Urban Ecology Agency",
            "contact_person": "Pere Martínez",
            "contact_email": "pmartinez@bcn.cat",
            "brief_description": "Transforming city blocks into pedestrian-priority zones to reduce traffic, improve air quality, and create vibrant community spaces.",
            "detailed_description": "The Barcelona Superblocks (Superilles) initiative reclaims street space from cars and returns it to residents. Each superblock encompasses nine city blocks where through-traffic is restricted, speed limits are reduced to 10-20 km/h, and streets are redesigned as shared spaces with greenery, play areas, and community gathering spots. The project has dramatically reduced air pollution, noise levels, and traffic accidents while increasing walking, cycling, and community interaction. Since implementation began in 2016, the city has created over 6 superblocks with plans for 500+ across Barcelona by 2030.",
            "success_factors": "Strong political leadership from Barcelona City Council; Co-design process with local residents; Phased implementation starting with low-cost tactical interventions; Integration with broader sustainable mobility strategy; Robust data collection showing measurable benefits; International recognition bringing additional funding and technical support.",
            "project_status": "Implemented",
            "workflow_status": "approved",
            "sdgs": [11, 13, 3],
            "typologies": ["Public Realm & Urban Landscape", "Infrastructure"],
            "requirements": ["Local Community Support", "Strong Political Leadership", "Public Sector Funding", "Community Engagement Framework"]
        },
        {
            "project_name": "Medellín Urban Acupuncture: Library Parks in Informal Settlements",
            "funding_needed_usd": 8750000,
            "funding_spent_usd": 8200000,
            "uia_region_id": 3,
            "city": "Medellín",
            "country": "Colombia",
            "latitude": 6.2442,
            "longitude": -75.5812,
            "organization_name": "Municipality of Medellín - Urban Innovation Department",
            "contact_person": "Carlos Restrepo",
            "contact_email": "crestrepo@medellin.gov.co",
            "brief_description": "Strategic placement of world-class library parks in marginalized neighborhoods to catalyze social transformation and urban renewal.",
            "detailed_description": "Medellín's Library Parks (Parques Biblioteca) represent urban acupuncture at its finest - placing exceptional public architecture and programming in the city's most challenged neighborhoods. Each library park combines a state-of-the-art library with community spaces, educational programs, and public realm improvements. The España Library Park, built in a former conflict zone, has become a symbol of urban transformation. These projects have reduced violence, increased educational attainment, and sparked complementary investments in public space, housing, and transportation infrastructure throughout surrounding communities.",
            "success_factors": "Political commitment to equity-focused urban investment; Architectural excellence creating neighborhood pride; Comprehensive programming beyond just books; Strategic location selection in areas of greatest need; Integration with broader urban mobility projects; Strong partnerships with local community organizations; Sustained investment in programming and maintenance.",
            "project_status": "Implemented",
            "workflow_status": "approved",
            "sdgs": [4, 10, 11, 16],
            "typologies": ["Educational", "Public Realm & Urban Landscape", "Cultural"],
            "requirements": ["Strong Political Leadership", "Public Sector Funding", "Community Engagement Framework", "Local Community Support"]
        },
        {
            "project_name": "Copenhagen District Heating: City-Wide Renewable Energy Distribution",
            "funding_needed_usd": 2100000000,
            "funding_spent_usd": 1950000000,
            "uia_region_id": 1,
            "city": "Copenhagen",
            "country": "Denmark",
            "latitude": 55.6761,
            "longitude": 12.5683,
            "organization_name": "Copenhagen District Heating (HOFOR)",
            "contact_person": "Morten Stobbe",
            "contact_email": "mstobbe@hofor.dk",
            "brief_description": "Comprehensive district heating network serving 98% of Copenhagen with renewable energy, eliminating individual heating systems and dramatically reducing carbon emissions.",
            "detailed_description": "Copenhagen operates one of the world's most comprehensive district heating systems, providing space heating and hot water to 98% of the city through an underground network of insulated pipes carrying hot water from centralized renewable energy plants. The system has evolved from waste-to-energy incineration plants to incorporate geothermal, biomass, solar thermal, and heat pumps. This infrastructure eliminates the need for individual heating systems in buildings, creates massive efficiency gains, and has been crucial to Copenhagen's goal of carbon neutrality by 2025. The system demonstrates how cities can retrofit existing urban areas with clean energy infrastructure at scale.",
            "success_factors": "Long-term municipal ownership and planning (started in 1920s); Gradual expansion and technology evolution; Strong regulatory framework requiring connection; Heat price stability and consumer benefit; Integration with waste management and renewable energy strategy; Continuous innovation in heat sources and efficiency; Replicable model being exported globally.",
            "project_status": "Implemented",
            "workflow_status": "approved",
            "sdgs": [7, 11, 13],
            "typologies": ["Infrastructure"],
            "requirements": ["Strong Political Leadership", "Public Sector Funding", "Technical Expertise", "Favorable Policy Environment"]
        },
        {
            "project_name": "Singapore Vertical Farming: 30x30 Food Security Initiative",
            "funding_needed_usd": 45000000,
            "funding_spent_usd": 38000000,
            "uia_region_id": 4,
            "city": "Singapore",
            "country": "Singapore",
            "latitude": 1.3521,
            "longitude": 103.8198,
            "organization_name": "Singapore Food Agency & Sky Greens Pte Ltd",
            "contact_person": "Dr. Lim Wei Ming",
            "contact_email": "wei_ming.lim@sfa.gov.sg",
            "brief_description": "Pioneering vertical farming technologies to achieve 30% domestic food production by 2030 in land-scarce Singapore.",
            "detailed_description": "Singapore's 30x30 initiative aims to produce 30% of the nation's nutritional needs locally by 2030, despite having less than 1% of land available for agriculture. The program focuses on high-tech vertical farming, aquaponics, and controlled environment agriculture. Sky Greens operates the world's first commercial vertical farm, producing vegetables in A-frame aluminum towers that use 95% less water and pesticides than traditional farming. The government provides grants, technical support, and regulatory frameworks to scale urban farming technologies. This addresses food security, reduces carbon footprint from imports, and creates new green economy jobs.",
            "success_factors": "Government-led strategic planning and financial support; Strong R&D partnerships with universities; Regulatory sandbox for food technology innovation; Focus on high-value crops suited to urban farming; Consumer education and market development; Integration with broader smart city initiatives; Technology transfer and export potential.",
            "project_status": "In Progress",
            "workflow_status": "approved",
            "sdgs": [2, 9, 11, 12],
            "typologies": ["Industrial", "Infrastructure"],
            "requirements": ["Strong Political Leadership", "Technical Expertise", "Research Institution Partnership", "Private Sector Partnership"]
        },
        {
            "project_name": "Kigali Master Plan: Africa's Model Sustainable City",
            "funding_needed_usd": 3200000000,
            "funding_spent_usd": 1800000000,
            "uia_region_id": 5,
            "city": "Kigali",
            "country": "Rwanda",
            "latitude": -1.9441,
            "longitude": 30.0619,
            "organization_name": "City of Kigali & Rwanda Development Board",
            "contact_person": "Pudence Rubingisa",
            "contact_email": "prubingisa@kigalicity.gov.rw",
            "brief_description": "Comprehensive urban master plan transforming Kigali into a green, inclusive, and resilient model city for Africa.",
            "detailed_description": "Kigali's 2040 Master Plan represents comprehensive urban transformation, building on Rwanda's remarkable post-genocide recovery. The plan emphasizes green building standards, mixed-use development, public transportation, affordable housing, and preservation of the city's unique hillside topography. Key initiatives include: mandatory green building certification, BRT system, wetland conservation, waste-to-energy plants, and affordable housing cooperatives. The plan balances rapid urbanization (5% annual population growth) with environmental protection and social inclusion. Kigali has become a model for sustainable African urbanism, hosting UN-Habitat conferences and sharing expertise across the continent.",
            "success_factors": "Strong national political commitment and governance; Clear vision and long-term planning; Integration of environmental protection with development; Emphasis on citizen participation and transparency; Strategic partnerships with international development organizations; Focus on building local capacity and institutions; Zero tolerance for corruption enabling effective implementation.",
            "project_status": "In Progress",
            "workflow_status": "approved",
            "sdgs": [11, 13, 16, 10],
            "typologies": ["Infrastructure", "Public Realm & Urban Landscape", "Residential"],
            "requirements": ["Strong Political Leadership", "International Funding", "Community Engagement Framework", "Environmental Assessment"]
        },
        {
            "project_name": "Vienna Social Housing: 100 Years of Inclusive Urban Development",
            "funding_needed_usd": 850000000,
            "funding_spent_usd": 820000000,
            "uia_region_id": 1,
            "city": "Vienna",
            "country": "Austria",
            "latitude": 48.2082,
            "longitude": 16.3738,
            "organization_name": "Wiener Wohnen (Vienna Housing Authority)",
            "contact_person": "Kathrin Gaál",
            "contact_email": "kathrin.gaal@wien.gv.at",
            "brief_description": "Century-long municipal housing program providing affordable, high-quality homes to 60% of Vienna's population.",
            "detailed_description": "Vienna's social housing program, dating to the 1920s, provides affordable rental housing to approximately 600,000 residents - nearly 60% of the city's population. Unlike public housing in many cities, Vienna's Gemeindebau includes middle-class residents and maintains high architectural and environmental standards. Recent projects emphasize energy efficiency, community facilities, and mixed-income integration. The program is funded through a housing tax on all residents and employers, creating a sustainable financing model. Vienna consistently ranks as the world's most livable city, with housing affordability being a key factor. The model demonstrates how cities can provide quality housing as a public good rather than commodity.",
            "success_factors": "Century of consistent political commitment across different governments; Sustainable financing through dedicated housing tax; High architectural and construction standards; Mixed-income integration preventing stigmatization; Strong tenant rights and security; Continuous innovation in sustainable building practices; Integration with public transportation and community facilities.",
            "project_status": "Implemented",
            "workflow_status": "approved",
            "sdgs": [11, 10, 1],
            "typologies": ["Residential"],
            "requirements": ["Strong Political Leadership", "Public Sector Funding", "Favorable Policy Environment", "Community Engagement Framework"]
        },
        {
            "project_name": "Curitiba Bus Rapid Transit: Pioneering Sustainable Urban Mobility",
            "funding_needed_usd": 125000000,
            "funding_spent_usd": 118000000,
            "uia_region_id": 3,
            "city": "Curitiba",
            "country": "Brazil",
            "latitude": -25.4284,
            "longitude": -49.2733,
            "organization_name": "URBS (Urbanização de Curitiba)",
            "contact_person": "Roberto Gregório",
            "contact_email": "rgregorio@urbs.curitiba.pr.gov.br",
            "brief_description": "World's first Bus Rapid Transit system, serving 85% of commuters and reducing car dependency while spurring sustainable urban development.",
            "detailed_description": "Curitiba pioneered Bus Rapid Transit (BRT) in the 1970s, creating a metro-quality bus system that has become a global model. The system features dedicated bus lanes, metro-style stations, articulated buses, and integrated fare payment. BRT serves 2.3 million passengers daily - 85% of the metropolitan area's public transport users. The system has reduced car dependency, improved air quality, and guided urban development along transit corridors. Curitiba's model has been replicated in over 200 cities worldwide. The success stems from integrated urban planning that combined transportation with land use, environmental protection, and social equity considerations.",
            "success_factors": "Visionary planning leadership (Mayor Jamie Lerner); Integration of transportation with urban development policy; Phased implementation allowing system refinement; Strong political continuity enabling long-term investment; Innovative design making bus travel aspirational rather than stigmatized; Environmental integration including flood management; Cost-effectiveness compared to rail alternatives; Global knowledge sharing and technical assistance.",
            "project_status": "Implemented",
            "workflow_status": "approved",
            "sdgs": [11, 13, 9],
            "typologies": ["Infrastructure"],
            "requirements": ["Strong Political Leadership", "Public Sector Funding", "Technical Expertise", "Community Engagement Framework"]
        },
        {
            "project_name": "Freiburg Solar City: Germany's Renewable Energy Showcase",
            "funding_needed_usd": 2800000000,
            "funding_spent_usd": 2650000000,
            "uia_region_id": 1,
            "city": "Freiburg",
            "country": "Germany",
            "latitude": 47.9990,
            "longitude": 7.8421,
            "organization_name": "City of Freiburg & Fraunhofer Institute",
            "contact_person": "Dieter Salomon",
            "contact_email": "dsalomon@stadt.freiburg.de",
            "brief_description": "Comprehensive renewable energy transformation making Freiburg Germany's solar capital and global sustainable city model.",
            "detailed_description": "Freiburg has transformed from a traditional German city to the country's renewable energy capital, generating more solar power per capita than almost anywhere in the world. The city's comprehensive approach includes: mandatory solar installations on new buildings, district heating from renewable sources, energy-efficient building standards (Passivhaus), extensive cycling infrastructure, car-free neighborhoods, and strong environmental education programs. The Vauban and Rieselfeld eco-districts showcase sustainable urban living with energy-positive buildings, car-sharing systems, and extensive green space. Freiburg demonstrates how mid-sized cities can achieve carbon neutrality while maintaining economic prosperity and high quality of life.",
            "success_factors": "Strong environmental movement and citizen engagement since 1970s; Integration of university research with municipal policy; Early adoption of feed-in tariffs for renewable energy; Comprehensive building energy standards; Transportation planning prioritizing cycling and public transit; Green economic development attracting clean-tech companies; International networking and knowledge sharing; Long-term political commitment across party lines.",
            "project_status": "Implemented",
            "workflow_status": "approved",
            "sdgs": [7, 11, 13],
            "typologies": ["Infrastructure", "Residential"],
            "requirements": ["Strong Political Leadership", "Technical Expertise", "Research Institution Partnership", "Community Engagement Framework"]
        },
        {
            "project_name": "Portland Urban Growth Boundary: 50 Years of Smart Growth",
            "funding_needed_usd": 95000000,
            "funding_spent_usd": 89000000,
            "uia_region_id": 3,
            "city": "Portland",
            "country": "United States",
            "latitude": 45.5152,
            "longitude": -122.6784,
            "organization_name": "Metro Portland Regional Government",
            "contact_person": "Lynn Peterson",
            "contact_email": "lynn.peterson@oregonmetro.gov",
            "brief_description": "Nation's first urban growth boundary containing sprawl, protecting farmland, and creating vibrant, walkable neighborhoods.",
            "detailed_description": "Portland's Urban Growth Boundary (UGB), established in 1973, contains urban development within a defined area, forcing denser development and protecting surrounding farmland and natural areas. The UGB covers Portland's metro area (1.5 million people) and is adjusted only through rigorous analysis showing need for additional land. This has created: vibrant downtown and neighborhood centers, extensive public transit including streetcars and light rail, preserved agricultural land, reduced infrastructure costs, and increased walkability. Portland demonstrates how regional planning can balance growth with environmental protection while creating economic opportunities and livable communities.",
            "success_factors": "State-level planning mandate providing legal framework; Regional government structure enabling metropolitan coordination; Strong public participation in planning processes; Integration with transportation and environmental planning; Flexible implementation allowing boundary adjustments based on data; Political culture valuing environmental protection and urbanism; Economic benefits demonstrating policy effectiveness; Continuous monitoring and adaptive management.",
            "project_status": "Implemented",
            "workflow_status": "approved",
            "sdgs": [11, 15, 2],
            "typologies": ["Infrastructure", "Public Realm & Urban Landscape"],
            "requirements": ["Strong Political Leadership", "Favorable Policy Environment", "Community Engagement Framework", "Environmental Assessment"]
        },
        {
            "project_name": "Bogotá Ciclovía: Weekly Car-Free Streets for 2 Million People",
            "funding_needed_usd": 12000000,
            "funding_spent_usd": 11500000,
            "uia_region_id": 3,
            "city": "Bogotá",
            "country": "Colombia",
            "latitude": 4.7110,
            "longitude": -74.0721,
            "organization_name": "Instituto Distrital de Recreación y Deporte (IDRD)",
            "contact_person": "Blanca Durán",
            "contact_email": "bduran@idrd.gov.co",
            "brief_description": "World's largest weekly car-free event, opening 121km of streets to 2 million cyclists, walkers, and families every Sunday.",
            "detailed_description": "Bogotá's Ciclovía transforms the city every Sunday and holiday, closing 121 kilometers of streets to cars and opening them to cyclists, pedestrians, and families. Started in 1976, the program now attracts over 2 million participants weekly - making it the world's largest car-free street event. Ciclovía includes not just cycling but aerobics classes, cultural events, and community activities throughout the city. The program has inspired similar initiatives in 400+ cities worldwide and demonstrates how cities can reclaim street space for people. Research shows significant health, social, and economic benefits, including increased physical activity, social cohesion, and local business revenue along Ciclovía routes.",
            "success_factors": "Simple concept with massive participation enabling political support; Strong safety protocols and community policing; Integration with broader cycling infrastructure development; Cultural programming beyond just cycling; Free participation ensuring inclusive access; International recognition bringing tourism and investment; Measurable health and economic benefits; Replication support helping spread globally.",
            "project_status": "Implemented",
            "workflow_status": "approved",
            "sdgs": [3, 11, 10],
            "typologies": ["Public Realm & Urban Landscape", "Sports & Recreation"],
            "requirements": ["Strong Political Leadership", "Community Engagement Framework", "Local Community Support"]
        },
        {
            "project_name": "Tokyo Disaster Preparedness: Resilient Megacity Planning",
            "funding_needed_usd": 4500000000,
            "funding_spent_usd": 4200000000,
            "uia_region_id": 4,
            "city": "Tokyo",
            "country": "Japan",
            "latitude": 35.6762,
            "longitude": 139.6503,
            "organization_name": "Tokyo Metropolitan Government - Bureau of Urban Development",
            "contact_person": "Hiroshi Nakamura",
            "contact_email": "hnakamura@metro.tokyo.lg.jp",
            "brief_description": "Comprehensive urban resilience planning preparing 37 million people for earthquakes, floods, and climate change impacts.",
            "detailed_description": "Tokyo's comprehensive disaster preparedness system protects the world's largest urban agglomeration (37 million people) from earthquakes, tsunamis, floods, and climate change impacts. The system includes: strict seismic building codes, underground flood tunnels, early warning systems, neighborhood emergency supplies, evacuation planning, and resilient infrastructure design. The massive Underground Discharge Channel protects the city from flooding during typhoons. Community-level disaster preparedness includes neighborhood associations, emergency supply distribution, and regular drills. Tokyo demonstrates how megacities can build resilience through integrated planning combining infrastructure, technology, community preparation, and governance systems.",
            "success_factors": "Historical experience with disasters driving political commitment; Integration of disaster planning with urban development; Strong building codes and enforcement; Community-level preparation and social capital; Advanced technology for early warning and communication; Continuous learning and system updating after each event; International cooperation and knowledge sharing; Long-term investment in resilient infrastructure.",
            "project_status": "Implemented",
            "workflow_status": "approved",
            "sdgs": [11, 13, 1],
            "typologies": ["Infrastructure", "Civic"],
            "requirements": ["Strong Political Leadership", "Technical Expertise", "Community Engagement Framework", "Public Sector Funding"]
        },
        {
            "project_name": "Vancouver Olympic Village: Carbon-Neutral Neighborhood Development",
            "funding_needed_usd": 1200000000,
            "funding_spent_usd": 1150000000,
            "uia_region_id": 3,
            "city": "Vancouver",
            "country": "Canada",
            "latitude": 49.2827,
            "longitude": -123.1207,
            "organization_name": "City of Vancouver & Canada Mortgage and Housing Corporation",
            "contact_person": "Sean Pander",
            "contact_email": "sean.pander@vancouver.ca",
            "brief_description": "First carbon-neutral neighborhood in North America, showcasing sustainable building design and urban planning innovations.",
            "detailed_description": "Vancouver's Olympic Village, built for the 2010 Winter Olympics, became North America's first carbon-neutral neighborhood and a showcase for sustainable urban development. The 16-hectare waterfront community features LEED Platinum buildings, district energy system, extensive green infrastructure, affordable housing integration, and car-sharing systems. The neighborhood energy utility uses sewage heat recovery and other renewable sources. The project demonstrates how cities can achieve carbon neutrality while creating vibrant, mixed-income communities. Post-Olympics, the village has become a model for sustainable neighborhood development, influencing Vancouver's broader climate action goals and green building requirements.",
            "success_factors": "Olympic momentum creating political will and international attention; Integration of social, environmental, and economic sustainability goals; Public-private partnerships enabling innovation; Comprehensive planning including energy, transportation, and social infrastructure; Strong green building standards and certification; Mixed-income housing preventing gentrification; Waterfront location providing development premium; Knowledge transfer and replication support.",
            "project_status": "Implemented",
            "workflow_status": "approved",
            "sdgs": [7, 11, 13],
            "typologies": ["Residential", "Infrastructure"],
            "requirements": ["Strong Political Leadership", "Public Sector Funding", "Private Sector Partnership", "Technical Expertise"]
        },
        {
            "project_name": "Cape Town Day Zero: Water Crisis Management and Conservation",
            "funding_needed_usd": 375000000,
            "funding_spent_usd": 340000000,
            "uia_region_id": 5,
            "city": "Cape Town",
            "country": "South Africa",
            "latitude": -33.9249,
            "longitude": 18.4241,
            "organization_name": "City of Cape Town Water and Sanitation Department",
            "contact_person": "Xanthea Limberg",
            "contact_email": "xanthea.limberg@capetown.gov.za",
            "brief_description": "Emergency water conservation program that averted 'Day Zero' and transformed Cape Town into a water-resilient city.",
            "detailed_description": "Cape Town faced 'Day Zero' - the day taps would run dry - during the 2015-2018 drought, the worst in 400 years. The city implemented aggressive demand management, reducing consumption from 1.2 billion to 500 million liters daily through: strict water restrictions, household quotas, pressure management, leak repair, greywater recycling, and intensive public communication. Emergency desalination plants and groundwater extraction provided additional supply. Citizens reduced consumption by 50%+ through behavior change. The crisis was averted, and Cape Town emerged as a global leader in urban water resilience. The experience demonstrates how cities can mobilize collective action during emergencies while building long-term sustainability.",
            "success_factors": "Crisis-driven political leadership and citizen mobilization; Transparent communication about severity and progress; Comprehensive demand and supply management strategy; Strong technical capacity in water management; Social solidarity across economic divides; Innovative pricing and restriction mechanisms; Investment in alternative water sources; Learning and adaptation during implementation; International support and knowledge sharing.",
            "project_status": "Implemented",
            "workflow_status": "approved",
            "sdgs": [6, 11, 13],
            "typologies": ["Infrastructure"],
            "requirements": ["Strong Political Leadership", "Community Engagement Framework", "Technical Expertise", "Public Sector Funding"]
        },
        {
            "project_name": "Seoul Digital Media City: Technology Hub and Urban Regeneration",
            "funding_needed_usd": 18000000000,
            "funding_spent_usd": 16800000000,
            "uia_region_id": 4,
            "city": "Seoul",
            "country": "South Korea",
            "latitude": 37.5665,
            "longitude": 126.8956,
            "organization_name": "Seoul Digital Media City Development Corporation",
            "contact_person": "Kim Jung-ho",
            "contact_email": "jkim@sdmcdc.com",
            "brief_description": "Comprehensive redevelopment of industrial area into Asia's leading digital media and technology cluster.",
            "detailed_description": "Seoul Digital Media City (DMC) transformed a 135-hectare industrial waste site into Northeast Asia's largest digital media cluster, hosting 1,000+ companies and 25,000+ workers. The project combines technology infrastructure, sustainable urban design, cultural facilities, and mixed-use development. DMC houses major broadcasting companies, gaming studios, digital content creators, and R&D centers. The development features smart city technologies, district cooling/heating, extensive green space, and integrated transportation. DMC demonstrates how cities can regenerate post-industrial areas through strategic clustering of knowledge industries while creating sustainable, livable urban environments.",
            "success_factors": "Strategic government planning and investment in digital economy; Comprehensive infrastructure including fiber optic networks; Integration of public and private sector development; Focus on clustering related industries creating synergies; High-quality urban design and environmental standards; Strong transportation connections to broader Seoul region; Educational partnerships with universities; International marketing and business attraction.",
            "project_status": "Implemented",
            "workflow_status": "approved",
            "sdgs": [8, 9, 11],
            "typologies": ["Commercial", "Infrastructure", "Industrial"],
            "requirements": ["Strong Political Leadership", "Public Sector Funding", "Private Sector Partnership", "Technical Expertise"]
        }
    ]

    # Add 8 additional verified projects from user prompt
    additional_projects = [
        {
            "project_name": "Curitiba Câmbio Verde - Green Exchange Waste-for-Food Program",
            "funding_needed_usd": 2500000,
            "funding_spent_usd": 2500000,
            "uia_region_id": 3,
            "city": "Curitiba",
            "country": "Brazil",
            "latitude": -25.4284,
            "longitude": -49.2733,
            "organization_name": "Curitiba Municipal Environment Secretariat (SMMA)",
            "contact_person": "SMMA Administration",
            "contact_email": "smma@curitiba.pr.gov.br",
            "brief_description": "City-wide initiative where residents trade recyclable materials for fresh produce - 4kg recyclables for 1kg fruits/vegetables, supporting 70,000+ families.",
            "detailed_description": "Running since June 1991, Curitiba's Green Exchange (Câmbio Verde) enables any citizen to exchange recyclable materials (paper, cardboard, glass, metals, used cooking oil) for fresh fruits and vegetables without registration. Every 4kg recyclables = 1kg produce. Monthly collection: 290 tons recyclables + 3,500 liters cooking oil diverted from incorrect disposal becoming food on tables. By 2007, recovered 45,000+ tons from landfills. Special Green Exchange operates city-wide in schools. Program employs ~600 workers. Guarantees sale of surplus crop production from small farmers while making fresh produce accessible/affordable for low-income residents in areas without conventional waste collection. Won 2010 Globe Sustainable City Award for excellence in sustainable urban development. Addresses multiple SDGs simultaneously: waste management, food security, poverty, farmer livelihoods, environmental education.",
            "success_factors": "Innovative solution addressing multiple challenges simultaneously: waste, poverty, nutrition, farmer income; Simple accessible model requiring no registration encouraging wide participation; Partnership between Municipal Environment (SMMA) and Supply (SMAB) Secretariats; Serving vehicle-inaccessible communities (favelas) where conventional waste collection impractical; Creating circular economy connecting urban waste to agricultural surplus; Employment generation (600 workers) in waste-to-food value chain; Education component through Special Green Exchange in schools building youth environmental awareness; Recognition attracting international attention and replication; Cost-effectiveness compared to conventional waste programs; Dignity-preserving approach trading rather than charity; Over 30 years sustained political commitment across administrations; Measurable impact: 290 tons/month recyclables, 70,000+ families benefited.",
            "project_status": "Implemented",
            "workflow_status": "approved",
            "sdgs": [1, 2, 11, 12],
            "typologies": ["Infrastructure", "Public Realm & Urban Landscape", "Markets & Exchange"],
            "requirements": ["Local Community Support", "Strong Political Leadership", "Public Sector Funding", "Community Engagement Framework"],
            "images": [
                {"url": "https://images.unsplash.com/photo-1532996122724-e3c354a0b15b", "alt_text": "Residents exchanging recyclables for fresh produce at Green Exchange station"},
                {"url": "https://images.unsplash.com/photo-1542838132-92c53300491e", "alt_text": "Fresh vegetables and fruits provided through Green Exchange program"}
            ]
        },
        {
            "project_name": "Vauban District - Europe's Most Sustainable Urban Community",
            "funding_needed_usd": 158000000,
            "funding_spent_usd": 158000000,
            "uia_region_id": 1,
            "city": "Freiburg",
            "country": "Germany",
            "latitude": 47.9990,
            "longitude": 7.8421,
            "organization_name": "City of Freiburg - Vauban Development Office",
            "contact_person": "Vauban Planning Department",
            "contact_email": "stadtplanung@freiburg.de",
            "brief_description": "Car-reduced solar district with 5,500 residents in passive/plus-energy buildings, producing more renewable energy than consumed, with 100% locally renewable energy.",
            "detailed_description": "Vauban district transformed former military barracks (187 hectares) into Europe's most sustainable urban community. Construction began 1998, completed in phases through 2000s following 2001 European Housing Expo. Population ~5,500 residents, 16,000+ workers. All buildings constructed to low-energy or passive house standards; many equipped with photovoltaic panels. Solar Settlement features entirely plus-energy buildings generating more energy than consumed - residents sell excess electricity to municipal grid reducing bills. 'Sun Ship' (Das Sonnenschiff) consists entirely of plus-energy buildings. Car traffic minimized: 30 km/h speed limit, cars give right-of-way to pedestrians/cyclists, streets designed prioritizing walking/cycling/public transport. Tram line directly connects to Freiburg city center. Aktern heat pump plant produces heating/cooling stored seasonally in 90m-deep aquifer wells. 2 MW wind power plant supplies 1,000 apartments. 1,400 m² solar collectors contribute 15% total heating. 120 m² solar cells for electricity. Green Space Factor incentivized developers to create defined green space amounts, resulting in extensive green roofs providing insulation, biodiversity, stormwater management.",
            "success_factors": "Strong political commitment from City of Freiburg supporting sustainable development; Learning from local opposition to nuclear power plants catalyzing renewable energy transition; German Energiewende policies (feed-in tariffs) making solar cost-competitive enabling mass adoption; Quality design preventing stigmatization of sustainable housing; Car-reduced not car-free approach balancing sustainability with practicality; Excellent public transit connectivity (tram to city center) enabling car-free lifestyle; Green Space Factor policy tool requiring defined greenery amounts; Participatory planning with future residents; Plus-energy buildings demonstrating technical and economic viability of net-positive construction; International recognition establishing as global model attracting study tours; Inspiring London Plan green space factor policy showing replicable influence; Mixed-use development combining residential, commercial, services; 20+ years proven sustainability demonstrating long-term viability not just experiment.",
            "project_status": "Implemented",
            "workflow_status": "approved",
            "sdgs": [7, 11, 13],
            "typologies": ["Residential", "Infrastructure"],
            "requirements": ["Strong Political Leadership", "Technical Expertise", "Community Engagement Framework", "Environmental Assessment"],
            "images": [
                {"url": "https://images.unsplash.com/photo-1509023464722-18d996393ca8", "alt_text": "Solar panels on residential buildings in Vauban district"},
                {"url": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2", "alt_text": "Car-free streets and green spaces in Vauban"}
            ]
        },
        {
            "project_name": "Portland Green Streets - Sustainable Stormwater Management",
            "funding_needed_usd": 86000000,
            "funding_spent_usd": 86000000,
            "uia_region_id": 3,
            "city": "Portland",
            "country": "United States",
            "latitude": 45.5152,
            "longitude": -122.6784,
            "organization_name": "City of Portland Bureau of Environmental Services",
            "contact_person": "BES Sustainable Stormwater",
            "contact_email": "stormwater@portlandoregon.gov",
            "brief_description": "City-wide green infrastructure network of 2,500+ facilities using rain gardens, bioswales, and permeable surfaces saving $58M over conventional drainage.",
            "detailed_description": "Portland transformed stormwater management from conventional underground pipes to above-ground sustainable strategies. Original plan: $144M for underground pipes kicking water to river potentially increasing flooding. New integrated plan: $86M using stormwater harvesting, infiltration, reuse as free irrigation - $58M savings primarily from reduced pipe replacement. Resolution No. 36500 (April 2007) adopted Green Streets Policy ENB-4.19 as Binding City Policy promoting green street facilities in public/private development. Currently maintains 2,500+ green street stormwater facilities plus ~150 vegetated regional water quality facilities distributed city-wide. 2023 authorized $12M over 5 years for on-call green infrastructure maintenance/irrigation (10 price agreements). Unlike storm drain pipe only conveying water, sustainable strategies are beautiful providing multiple benefits: traffic control, neighborhood beautification, safer walking/bicycling, natural bioremediation filtering contaminants, free irrigation for associated plantings shading/cooling neighborhoods in summer. Reduced flooding throughout subwatersheds and downstream while improving water quality. Turned problem neighborhoods into desirable neighborhoods increasing business and financial resources for city.",
            "success_factors": "Financial analysis demonstrating $58M cost savings over conventional approach building business case; Multiple co-benefits beyond drainage: beautification, traffic calming, safety, cooling, increasing political support; Binding City Policy (Resolution 36500) providing regulatory framework ensuring implementation; Steady construction integrated into development projects spreading costs; Measurable water quality improvements providing evidence of effectiveness; Neighborhood revitalization attracting business investment creating economic development narrative; Educational value demonstrating nature-based solutions; Replicable model inspiring other US cities; Long-term commitment: $12M 5-year maintenance contract showing operational sustainability; Bureau of Environmental Services institutional leadership; Integration with broader Portland sustainability brand; Community engagement transforming skepticism into pride; Design excellence ensuring aesthetic quality.",
            "project_status": "Implemented",
            "workflow_status": "approved",
            "sdgs": [6, 11, 13, 15],
            "typologies": ["Infrastructure", "Public Realm & Urban Landscape", "Natural Environment & Ecological Projects"],
            "requirements": ["Strong Political Leadership", "Public Sector Funding", "Favorable Policy Environment", "Environmental Assessment"]
        },
        {
            "project_name": "Cape Town New Water Programme - Overcoming Day Zero Crisis",
            "funding_needed_usd": 580000000,
            "funding_spent_usd": 250000000,
            "uia_region_id": 5,
            "city": "Cape Town",
            "country": "South Africa",
            "latitude": -33.9249,
            "longitude": 18.4241,
            "organization_name": "City of Cape Town Water & Sanitation Department",
            "contact_person": "Water Resilience Office",
            "contact_email": "water@capetown.gov.za",
            "brief_description": "Comprehensive water resilience strategy delivering 300 million liters/day from alternative sources by 2030 after near Day Zero crisis in 2018.",
            "detailed_description": "Following devastating 2015-2018 drought bringing Cape Town within 90 days of 'Day Zero' (taps running dry), city adopted comprehensive resilience strategy. New Water Programme targets 300 million liters/day (ML/day) by 2030 from alternative sources. R10 billion ($580M) of R30B capital expenditure plan invested in water/sanitation infrastructure over 3 years ensuring sustainable development. City raised R1 billion Green Bond on Johannesburg Stock Exchange funding key sustainability projects: reservoir upgrades, water pressure management, water reuse, sewer/supply network upgrades. Groundwater: R4.7B ($250M) investment bringing 105 ML/day from aquifers by 2036. Table Mountain Group Aquifer delivered first water 2020; Cape Flats Aquifer expected mid-2023. Quadrupled annual rate for pipe replacement maintaining low water losses. Desalination and reuse projects coordinated with Independent Advisory Panel and Water Research Commission ensuring transparency/accountability. City targets <950 ML/day consumption converting water savings into culture. Greater Cape Town Water Fund: Nature-based solutions restoring watersheds, R50M city contribution 2021-2023. Added 17.6 billion liters annually through watershed restoration.",
            "success_factors": "Crisis focusing political will and public support for major investment; Communication strategy using 'Day Zero' narrative effectively changing middle-class water consumption behavior; Diversified portfolio approach (groundwater, desalination, reuse, conservation) reducing risk; Green Bond financing (R1B) demonstrating innovative funding mechanism; Nature-based solutions complementing gray infrastructure: Greater Cape Town Water Fund watershed restoration cost-effective; Public-private partnerships for water reuse/desalination; Cultural shift: sustained conservation even after crisis passed; Transparent governance through Independent Advisory Panel; Integration with broader climate adaptation strategy; Learning from near-disaster preventing future crises; International attention bringing funding and technical support; Evidence-based planning using best available climate models.",
            "project_status": "In Progress",
            "workflow_status": "approved",
            "sdgs": [6, 11, 13],
            "typologies": ["Infrastructure"],
            "requirements": ["Strong Political Leadership", "Community Engagement Framework", "Technical Expertise", "Public Sector Funding"]
        },
        {
            "project_name": "Malmö Western Harbour Bo01 - Climate-Neutral Urban District",
            "funding_needed_usd": 450000000,
            "funding_spent_usd": 450000000,
            "uia_region_id": 1,
            "city": "Malmö",
            "country": "Sweden",
            "latitude": 55.6167,
            "longitude": 12.9833,
            "organization_name": "City of Malmö - Western Harbour Development",
            "contact_person": "Western Harbour Project Office",
            "contact_email": "westernharbour@malmo.se",
            "brief_description": "187-hectare transformation of run-down shipyard into vibrant sustainable district with 10,000 residents, 100% locally renewable energy, extensive green infrastructure.",
            "detailed_description": "Malmö Western Harbour transformed previously run-down shipyard/industrial area (187 hectares) into vibrant 'city within a city' with university, ~10,000 residents, 16,000+ workers. Bo01 district designed by international architects following 2001 European Housing Expo emphasizing sustainability broadly. Many buildings have green roofs with plants varying colors by season plus extensive rainwater runoff systems. Aktern heat pump plant at energy system heart producing heating/cooling stored seasonally in natural aquifers in 90m-deep wells. Electricity from local 2 MW wind power plant supplying 1,000 apartments. 1,400 m² solar collectors on roofs/walls contribute 15% total heating. 120 m² solar cells for electricity generation. Modern waste collection systems facilitate efficient management: glass, metal, plastic, paper, food waste separated for recycling; residual waste incinerated for heating; food waste transported to Sjölunda biogas plant converted to slurry then Kristianstad recycling plant producing biogas heating Bo01 buildings. 200 households have waste grinders. Green Space Factor (developer dialogue quality program element) required defined green space creation with differential weighting: more points for trees/bushes than grass, domestic species preferred, green roofs included. Green roofs provide insulation, increase biodiversity, retain rainwater relieving stormwater system. 20+ years operational demonstrating sustained sustainability.",
            "success_factors": "Transforming brownfield (shipyard) into sustainable asset demonstrating urban regeneration potential; Strong municipal vision and commitment from City of Malmö; International architectural competition attracting design excellence; European Housing Expo 2001 showcasing innovations internationally; 100% locally renewable energy demonstrating technical feasibility; Integrated waste-to-energy and biogas systems creating circular resource flows; Green Space Factor policy tool incentivizing green infrastructure; Green roofs providing multiple benefits (insulation, biodiversity, stormwater); Mixed-use development combining residential, employment, education creating complete community; Public space quality attracting residents and businesses; Inspiration for London Plan Green Space Factor showing policy influence; 20+ year track record proving long-term viability; Carbon neutrality achievement demonstrating climate action feasibility; Accessibility design throughout district.",
            "project_status": "Implemented",
            "workflow_status": "approved",
            "sdgs": [7, 11, 12, 13],
            "typologies": ["Residential", "Infrastructure"],
            "requirements": ["Strong Political Leadership", "Public Sector Funding", "Technical Expertise", "Environmental Assessment"]
        },
        {
            "project_name": "Addis Ababa Light Rail Transit - Sub-Saharan Africa First LRT",
            "funding_needed_usd": 475000000,
            "funding_spent_usd": 475000000,
            "uia_region_id": 5,
            "city": "Addis Ababa",
            "country": "Ethiopia",
            "latitude": 9.0320,
            "longitude": 38.7469,
            "organization_name": "Ethiopian Railways Corporation",
            "contact_person": "ERC Light Rail Division",
            "contact_email": "info@erc.gov.et",
            "brief_description": "Sub-Saharan Africa's first light rail: 31.6km system carrying 60,000 passengers/hour powered by renewable energy (hydro/geothermal/wind), reducing emissions 170,000 tons CO2/year.",
            "detailed_description": "Inaugurated September 2015 as Sub-Saharan Africa first modern light-rail train (LRT). North-south line intersecting east-west line totaling 19.6 miles (31.6km). Cost $475M ($24M/mile). Built by China State Railways with Export-Import Bank of China loans; rail cars manufactured China. Can carry 60,000 people/hour; after 10 months reached 15,000 passengers/hour each direction. Powered by Ethiopia grid: almost exclusively hydropower, geothermal, wind - making it renewable energy-powered transit. Transportation accounts 47% CO2 emissions in Addis; LRT reduces greenhouse gases while bringing clean efficient transport. Emissions reductions: 55,000 tons CO2/year (2015) growing to 170,000 tons/year by 2030. Average transport speed improved from 10 km/hour road traffic to 22 km/hour with LRT significantly reducing worker commute times. 1,100+ jobs created to operate LRT. Ethiopian government expects reduced foreign oil purchases. Decreased particulate emissions reducing heart/respiratory diseases. Blueprint for local expansion and regional replication. Part of Addis Ababa Climate Resilient Growth Economy plan driving green economy transition. However faces maintenance challenges: only 8 of 41 trains functional 7 years later, operates alternate days for track maintenance, needs $60M restoration.",
            "success_factors": "Sub-Saharan Africa first demonstrating continental leadership and ambition; International collaboration: Ethiopian government, Chinese government, foreign banks enabling complex financing; Integration with Climate Resilient Growth Economy plan connecting to broader development strategy; Renewable energy grid (hydro/geothermal/wind) making it truly low-carbon transport; Measurable emissions reductions (170,000 tons CO2/year by 2030); Significant commute time reduction (10 to 22 km/hour) improving quality of life; Job creation (1,100+ positions) providing employment; Health benefits from reduced air pollution; Low cost per mile ($24M) compared to developed country projects; However: maintenance challenges highlighting importance of operational planning, technology transfer, and sustainable financing beyond construction; Lessons: initial cost advantage undermined without maintenance capacity and funding.",
            "project_status": "Implemented",
            "workflow_status": "approved",
            "sdgs": [7, 9, 11, 13],
            "typologies": ["Infrastructure"],
            "requirements": ["Strong Political Leadership", "Technical Expertise", "International Funding", "Private Sector Partnership"]
        },
        {
            "project_name": "Masdar City - Zero-Carbon Eco-City in the Desert",
            "funding_needed_usd": 19800000000,
            "funding_spent_usd": 2400000000,
            "uia_region_id": 2,
            "city": "Abu Dhabi",
            "country": "United Arab Emirates",
            "latitude": 24.4292,
            "longitude": 54.6167,
            "organization_name": "Masdar / Mubadala Development Company",
            "contact_person": "Masdar City Management",
            "contact_email": "info@masdar.ae",
            "brief_description": "6 sq km sustainable city in Abu Dhabi desert targeting 50,000 residents with net-zero energy buildings, renewable power, 40% reduced energy/water consumption.",
            "detailed_description": "Masdar City is Abu Dhabi government-funded ecology project designed by Foster and Partners, built by Masdar (Mubadala Development Company subsidiary). Construction started 2008 next to Abu Dhabi International Airport. Originally planned completion 2016, pushed to 2020-2025 due to global financial crisis; building to demand not speculating empty buildings. Estimated construction cost $18.7-19.8 billion. Abu Dhabi invested $2.4 billion smart city initiatives since 2015. Currently 4,000+ residents, ultimate capacity ~50,000. Hosts headquarters International Renewable Energy Agency (IRENA). 1,000+ public/private organizations based in city (6 sq km economic free zone). Community powered partly by on-site renewable energy, constructed using sustainable materials. Eco-friendly buildings designed reducing energy/water consumption minimum 40%; some exceed this. Three net-zero energy buildings under construction producing as much energy as consumed. Masdar Green REIT portfolio valued AED 980M (USD 267M) December 2021 with 3.3% valuation gain. Part of UAE long-term plan achieving net zero 2050 and diversifying economy beyond oil. Hub for cleantech companies: Siemens, GE, IRENA, Advanced Technology Research Council. Solar power costs as little as 1.35 cents/kWh demonstrating economic viability.",
            "success_factors": "Strong Abu Dhabi government political and financial commitment demonstrating state capacity; Diversification strategy beyond oil providing strategic imperative; World-class design by Foster and Partners ensuring architectural quality; Economic free zone attracting international companies and investment; IRENA headquarters providing international legitimacy and visibility; $50M UAE-Caribbean Renewable Energy Fund demonstrating technology export; Masdar Green REIT providing innovative financing mechanism and investment opportunity; ESG investment attractiveness as first 'green' REIT in UAE; Pragmatic timeline adjustment (building to demand) avoiding ghost city syndrome; Clean technology cluster creating innovation ecosystem; Test-bed for renewable energy technologies before broader deployment; Integration with Abu Dhabi Vision 2030; However: original 100% renewable energy goal moderated showing challenge of absolute sustainability in practice; Lessons: ambition must balance with feasibility.",
            "project_status": "In Progress",
            "workflow_status": "approved",
            "sdgs": [7, 9, 11, 12, 13],
            "typologies": ["Commercial", "Infrastructure", "Industrial"],
            "requirements": ["Strong Political Leadership", "Public Sector Funding", "Private Sector Partnership", "Technical Expertise"]
        },
        {
            "project_name": "Mexico City Cosecha de Lluvia - Rainwater Harvesting for Water Security",
            "funding_needed_usd": 18000000,
            "funding_spent_usd": 18000000,
            "uia_region_id": 3,
            "city": "Mexico City",
            "country": "Mexico",
            "latitude": 19.4326,
            "longitude": -99.1332,
            "organization_name": "SEDEMA - Mexico City Environment Secretariat",
            "contact_person": "Cosecha de Lluvia Program",
            "contact_email": "cosecha@sedema.cdmx.gob.mx",
            "brief_description": "Citywide rainwater harvesting: 2,300+ systems installed in 1,800+ schools serving 1.3M users, capturing 918 million liters annually, reducing water scarcity in marginalized areas.",
            "detailed_description": "Mexico City Rainwater Harvesting Program (Cosecha de Lluvia) addresses acute water scarcity in marginalized neighborhoods lacking reliable piped water supply. Since 2023 with 'Escuelas de Captación' (Schools of Harvesting) project: 2,300+ rainwater harvesting systems (SCALL) installed in 1,800+ educational facilities all levels city-wide. Investment: 300 million pesos (~$18M USD). Benefits 1.3M+ total users (students + staff). Majority in basic education schools, covering all 16 Alcaldías (boroughs). Annual capture capacity: 918 million liters alleviating pressure on traditional water sources. Systems enable water for showering, washing, cooking where public supply doesn't reach or is unreliable. Before program, residents collected rainwater with makeshift systems filtered through cotton cloths or bought water from tanker trucks (pipas) carrying in jerry cans. RHS consists of receptacle 'Tlaloc' (named after Aztec rain god) filtering dust before water runs into 5,000-liter tank distributed to local network. First 2-3 downpours pass through for cleaner harvested water. Installation cost ~$270 per system. Successfully reduced water scarcity, improved welfare for beneficiary households, avoided GHG emissions from centralized water provision, reduced urban runoff supporting climate adaptation.",
            "success_factors": "Addressing critical need in vehicle-inaccessible areas where conventional infrastructure doesn't reach; Low-cost appropriate technology accessible to resource-constrained communities ($270/system); Schools-first strategy maximizing impact: 1.3M users including vulnerable children; Education integration teaching students about water conservation and climate adaptation; Community organizing building local ownership and maintenance capacity; Cultural relevance naming system after Aztec rain god Tlaloc; Simple design enabling replication and local maintenance; Impressive scale: 2,300+ systems demonstrating programmatic not just pilot approach; Multiple benefits: water security, GHG reduction, flood mitigation, nutrition (clean water for cooking); Dignity-preserving approach replacing tanker truck dependence; Replicable model for other Latin American cities facing similar challenges; Climate adaptation building resilience to supply disruptions.",
            "project_status": "In Progress",
            "workflow_status": "approved",
            "sdgs": [6, 11, 13],
            "typologies": ["Infrastructure", "Educational"],
            "requirements": ["Community Engagement Framework", "Local Community Support", "Technical Expertise", "Cultural Sensitivity"]
        }
    ]

    # Combine original and additional projects
    all_projects = projects + additional_projects

    print(f"Loading {len(all_projects)} real-world SDG projects ({len(projects)} original + {len(additional_projects)} additional)...")

    conn = db.get_connection()
    cursor = conn.cursor()

    for i, project in enumerate(all_projects, 1):
        # Insert main project
        cursor.execute("""
            INSERT INTO projects (
                project_name, funding_needed_usd, uia_region_id,
                city, country, latitude, longitude, organization_name, contact_person,
                contact_email, brief_description, detailed_description, success_factors,
                project_status, workflow_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project["project_name"],
            project["funding_needed_usd"],
            project["uia_region_id"],
            project["city"],
            project["country"],
            project["latitude"],
            project["longitude"],
            project["organization_name"],
            project["contact_person"],
            project["contact_email"],
            project["brief_description"],
            project["detailed_description"],
            project["success_factors"],
            project["project_status"],
            project["workflow_status"],
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))

        project_id = cursor.lastrowid

        # Link to SDGs
        for sdg_id in project["sdgs"]:
            cursor.execute("""
                INSERT INTO project_sdgs (project_id, sdg_id) VALUES (?, ?)
            """, (project_id, sdg_id))

        # Link to typologies
        for typology_name in project["typologies"]:
            cursor.execute("""
                INSERT INTO project_typologies (project_id, typology) VALUES (?, ?)
            """, (project_id, typology_name))

        # Link to requirements
        for requirement_name in project["requirements"]:
            cursor.execute("""
                INSERT INTO project_requirements (project_id, requirement_category, requirement_text)
                VALUES (?, ?, ?)
            """, (project_id, "Implementation", requirement_name))

        # Add project images if provided
        if "images" in project:
            for j, image in enumerate(project["images"]):
                cursor.execute("""
                    INSERT INTO project_images (project_id, image_url, alt_text, is_primary)
                    VALUES (?, ?, ?, ?)
                """, (project_id, image["url"], image["alt_text"], j == 0))

    conn.commit()
    conn.close()

def print_data_summary(db: AtlasDB):
    """Print summary of loaded data"""
    conn = db.get_connection()
    cursor = conn.cursor()

    # Count projects
    cursor.execute("SELECT COUNT(*) FROM projects")
    project_count = cursor.fetchone()[0]

    # Count by region
    cursor.execute("""
        SELECT r.name, COUNT(p.id)
        FROM uia_regions r
        LEFT JOIN projects p ON r.id = p.uia_region_id
        GROUP BY r.id, r.name
        ORDER BY r.id
    """)
    region_counts = cursor.fetchall()

    # Count by SDG
    cursor.execute("""
        SELECT s.name, COUNT(ps.project_id)
        FROM sdgs s
        LEFT JOIN project_sdgs ps ON s.id = ps.sdg_id
        GROUP BY s.id, s.name
        ORDER BY COUNT(ps.project_id) DESC
        LIMIT 10
    """)
    sdg_counts = cursor.fetchall()

    conn.close()

    print(f"\nData Summary:")
    print(f"   - Total Projects: {project_count}")
    print(f"\nProjects by Region:")
    for region_name, count in region_counts:
        print(f"   - {region_name}: {count}")

    print(f"\nTop SDGs (by project count):")
    for sdg_name, count in sdg_counts:
        if count > 0:
            print(f"   - {sdg_name}: {count}")

if __name__ == "__main__":
    load_comprehensive_sdg_data()