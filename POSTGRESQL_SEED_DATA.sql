-- ============================================================================
-- SEED DATA FOR ATLAS 3+3 DATABASE
-- ============================================================================

-- Insert UIA Regions
INSERT INTO uia_regions (region_id, region_name, region_code, region_description) VALUES
(1, 'Region I - Western Europe', 'WE', 'Western European countries including UK, France, Germany, Spain, Italy, and Nordic countries'),
(2, 'Region II - Central and Eastern Europe and Middle East', 'MEEE', 'Central/Eastern Europe, Russia, Turkey, and Middle Eastern countries'),
(3, 'Region III - The Americas', 'AM', 'North, Central, and South American countries'),
(4, 'Region IV - Asia and Oceania', 'AO', 'Asian countries including China, Japan, India, Southeast Asia, Australia, and Pacific Islands'),
(5, 'Region V - Africa', 'AF', 'All African countries including North Africa, Sub-Saharan Africa, and island nations');

-- Insert 17 SDGs with official UN colors and metadata
INSERT INTO sdgs (sdg_number, sdg_name, sdg_short_name, sdg_color_hex, sdg_color_pantone, sdg_icon_url, sdg_description) VALUES
(1, 'No Poverty', 'No Poverty', '#E5243B', '185 C', 'https://archium.ateneo.edu/un-sdg-icons/1/', 'End poverty in all its forms everywhere'),
(2, 'Zero Hunger', 'Zero Hunger', '#DDA63A', '7555 C', 'https://archium.ateneo.edu/un-sdg-icons/2/', 'End hunger, achieve food security and improved nutrition and promote sustainable agriculture'),
(3, 'Good Health and Well-Being', 'Good Health', '#4C9F38', '7739 C', 'https://archium.ateneo.edu/un-sdg-icons/3/', 'Ensure healthy lives and promote well-being for all at all ages'),
(4, 'Quality Education', 'Quality Education', '#C5192D', '200 C', 'https://archium.ateneo.edu/un-sdg-icons/4/', 'Ensure inclusive and equitable quality education and promote lifelong learning opportunities for all'),
(5, 'Gender Equality', 'Gender Equality', '#FF3A21', 'BRIGHT RED C', 'https://archium.ateneo.edu/un-sdg-icons/5/', 'Achieve gender equality and empower all women and girls'),
(6, 'Clean Water and Sanitation', 'Clean Water', '#26BDE2', '638 C', 'https://archium.ateneo.edu/un-sdg-icons/6/', 'Ensure availability and sustainable management of water and sanitation for all'),
(7, 'Affordable and Clean Energy', 'Clean Energy', '#FCC30B', '1235 C', 'https://archium.ateneo.edu/un-sdg-icons/7/', 'Ensure access to affordable, reliable, sustainable and modern energy for all'),
(8, 'Decent Work and Economic Growth', 'Economic Growth', '#A21942', '1955 C', 'https://archium.ateneo.edu/un-sdg-icons/8/', 'Promote sustained, inclusive and sustainable economic growth, full and productive employment and decent work for all'),
(9, 'Industry, Innovation and Infrastructure', 'Infrastructure', '#FD6925', '1585 C', 'https://archium.ateneo.edu/un-sdg-icons/9/', 'Build resilient infrastructure, promote inclusive and sustainable industrialization and foster innovation'),
(10, 'Reduced Inequalities', 'Reduced Inequalities', '#DD1367', '219 C', 'https://archium.ateneo.edu/un-sdg-icons/10/', 'Reduce inequality within and among countries'),
(11, 'Sustainable Cities and Communities', 'Sustainable Cities', '#FD9D24', '1375 C', 'https://archium.ateneo.edu/un-sdg-icons/11/', 'Make cities and human settlements inclusive, safe, resilient and sustainable'),
(12, 'Responsible Consumption and Production', 'Responsible Consumption', '#BF8B2E', '131 C', 'https://archium.ateneo.edu/un-sdg-icons/12/', 'Ensure sustainable consumption and production patterns'),
(13, 'Climate Action', 'Climate Action', '#3F7E44', '7742 C', 'https://archium.ateneo.edu/un-sdg-icons/13/', 'Take urgent action to combat climate change and its impacts'),
(14, 'Life Below Water', 'Life Below Water', '#0A97D9', '7461 C', 'https://archium.ateneo.edu/un-sdg-icons/14/', 'Conserve and sustainably use the oceans, seas and marine resources for sustainable development'),
(15, 'Life on Land', 'Life on Land', '#56C02B', '361 C', 'https://archium.ateneo.edu/un-sdg-icons/15/', 'Protect, restore and promote sustainable use of terrestrial ecosystems, sustainably manage forests, combat desertification'),
(16, 'Peace, Justice and Strong Institutions', 'Peace & Justice', '#00689D', '7462 C', 'https://archium.ateneo.edu/un-sdg-icons/16/', 'Promote peaceful and inclusive societies for sustainable development, provide access to justice for all'),
(17, 'Partnerships for the Goals', 'Partnerships', '#19486A', '294 C', 'https://archium.ateneo.edu/un-sdg-icons/17/', 'Strengthen the means of implementation and revitalize the global partnership for sustainable development');

-- Insert Typologies
INSERT INTO typologies (typology_code, typology_name, typology_description, display_order) VALUES
('residential', 'Residential', 'Housing and residential communities', 1),
('commercial', 'Commercial', 'Commercial and retail developments', 2),
('educational', 'Educational', 'Schools, universities, training facilities', 3),
('healthcare', 'Healthcare', 'Hospitals, clinics, health centers', 4),
('civic', 'Civic', 'Government buildings, administrative facilities', 5),
('cultural', 'Cultural', 'Museums, theaters, cultural centers', 6),
('sports', 'Sports & Recreation', 'Sports facilities, recreation centers', 7),
('industrial', 'Industrial', 'Manufacturing, industrial facilities', 8),
('infrastructure', 'Infrastructure', 'Transportation, utilities, public works', 9),
('public_realm', 'Public Realm', 'Parks, plazas, public spaces', 10),
('natural_environment', 'Natural Environment', 'Conservation, ecological restoration', 11),
('markets', 'Markets & Exchange', 'Markets, trade facilities', 12),
('other', 'Other', 'Other project types', 99);

-- Insert Requirements
INSERT INTO requirements (requirement_code, requirement_name, requirement_category, requirement_description, display_order) VALUES
-- Funding Requirements
('private_investment', 'Private Investment', 'funding', 'Investment from private sector entities', 1),
('public_funding', 'Public Funding', 'funding', 'Government budget allocations and public funds', 2),
('intl_aid', 'International Aid', 'funding', 'Development assistance from international organizations', 3),
('community_funding', 'Community Funding', 'funding', 'Local community fundraising and contributions', 4),
('philanthropic', 'Philanthropic Grants', 'funding', 'Grants from foundations and charitable organizations', 5),
-- Government & Regulatory Requirements
('govt_support', 'Government Support', 'government_regulatory', 'National government backing and support', 6),
('regional_support', 'Regional Support', 'government_regulatory', 'Regional or state government support', 7),
('local_support', 'Local Support', 'government_regulatory', 'Municipal or local government support', 8),
('favorable_policies', 'Favorable Policies', 'government_regulatory', 'Supportive policy and regulatory framework', 9),
('permitting', 'Permitting & Approvals', 'government_regulatory', 'Required permits and regulatory approvals', 10),
-- Other Requirements
('leadership', 'Strong Leadership', 'other', 'Committed leadership and project champions', 11),
('media_coverage', 'Media & Public Support', 'other', 'Public awareness and media attention', 12),
('land_availability', 'Land Availability', 'other', 'Access to suitable land or property', 13),
('other', 'Other Requirements', 'other', 'Additional project-specific requirements', 99);

-- Insert Sample Users
INSERT INTO users (user_id, email, full_name, role, organization_affiliation, is_active) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'admin@atlas3plus3.org', 'Maria Rodriguez', 'admin', 'UIA - International Union of Architects', true),
('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'reviewer1@atlas3plus3.org', 'Jean-Paul Dubois', 'reviewer', 'UIA Region I - Western Europe', true),
('c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'reviewer2@atlas3plus3.org', 'Fatima Al-Hassan', 'reviewer', 'UIA Region II - MEEE', true),
('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380a44', 'submitter1@gmail.com', 'Carlos Mendez', 'submitter', 'Urban Planning Consultancy - São Paulo', true),
('e4eebc99-9c0b-4ef8-bb6d-6bb9bd380a55', 'submitter2@gmail.com', 'Aisha Okonkwo', 'submitter', 'Green Africa Foundation', true),
('f5eebc99-9c0b-4ef8-bb6d-6bb9bd380a66', 'submitter3@gmail.com', 'Li Wei', 'submitter', 'Sustainable Cities Initiative - Beijing', true);

-- ============================================================================
-- SAMPLE PROJECTS (20 diverse examples covering all regions)
-- ============================================================================

-- PROJECT 1: Barcelona Superblocks (Western Europe - Spain)
INSERT INTO projects (
    project_id, project_name, project_slug, organization_name, contact_person, contact_email,
    project_status, city, country, region_id, geolocation,
    funding_needed_usd, funding_spent_usd, brief_description, detailed_description, success_factors,
    workflow_status, approval_date, published_date, created_by_user_id, last_reviewed_by_user_id
) VALUES (
    '10000000-0000-0000-0000-000000000001',
    'Barcelona Superblocks: Urban Regeneration for Livable Streets',
    'barcelona-superblocks-urban-regeneration',
    'Barcelona City Council - Urban Ecology Agency',
    'Pere Martínez',
    'pmartinez@bcn.cat',
    'Implemented',
    'Barcelona',
    'Spain',
    1, -- Western Europe
    ST_SetSRID(ST_MakePoint(2.1734, 41.3851), 4326),
    12500000.00, 11200000.00,
    'Transforming city blocks into pedestrian-priority zones to reduce traffic, improve air quality, and create vibrant community spaces.',
    'The Barcelona Superblocks (Superilles) initiative reclaims street space from cars and returns it to residents. Each superblock encompasses nine city blocks where through-traffic is restricted, speed limits are reduced to 10-20 km/h, and streets are redesigned as shared spaces with greenery, play areas, and community gathering spots. The project has dramatically reduced air pollution, noise levels, and traffic accidents while increasing walking, cycling, and community interaction. Since implementation began in 2016, the city has created over 6 superblocks with plans for 500+ across Barcelona by 2030. The model combines tactical urbanism with long-term infrastructure investment.',
    'Key success factors include: Strong political leadership from Barcelona City Council; Co-design process with local residents ensuring community buy-in; Phased implementation starting with low-cost tactical interventions (painted crossings, planters) before permanent infrastructure; Integration with broader sustainable mobility strategy including bike lanes and public transit improvements; Robust data collection showing measurable benefits in air quality, noise reduction, and public health; International recognition bringing additional funding and technical support.',
    'approved',
    '2024-03-15 10:30:00+00',
    '2024-03-20 09:00:00+00',
    'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380a44',
    'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22'
);

-- [Continue with remaining 19 projects using the same format, updating coordinates to use PostGIS format]

-- ============================================================================
-- LINK PROJECTS TO SDGs, TYPOLOGIES, AND REQUIREMENTS
-- ============================================================================

-- Barcelona Superblocks → SDG 11 (Sustainable Cities), 13 (Climate Action), 3 (Health)
INSERT INTO project_sdgs (project_id, sdg_id) VALUES
('10000000-0000-0000-0000-000000000001', 11),
('10000000-0000-0000-0000-000000000001', 13),
('10000000-0000-0000-0000-000000000001', 3);

-- Barcelona Superblocks → Typologies
INSERT INTO project_typologies (project_id, typology_code) VALUES
('10000000-0000-0000-0000-000000000001', 'public_realm'),
('10000000-0000-0000-0000-000000000001', 'infrastructure');

-- Barcelona Superblocks → Requirements
INSERT INTO project_requirements (project_id, requirement_code) VALUES
('10000000-0000-0000-0000-000000000001', 'local_support'),
('10000000-0000-0000-0000-000000000001', 'public_funding'),
('10000000-0000-0000-0000-000000000001', 'leadership'),
('10000000-0000-0000-0000-000000000001', 'favorable_policies');

-- [Additional project mappings would continue here...]