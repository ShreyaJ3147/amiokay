-- ============================================
-- AmIOkay Database Schema
-- ============================================
-- An anonymized women's health symptom comparison tool
-- that helps users understand their symptoms and find
-- the right type of specialist.
-- ============================================


-- ============================================
-- 1. SYMPTOM CATEGORIES & SYMPTOMS
-- ============================================
-- Categories group symptoms so the quiz UI isn't overwhelming.
-- e.g., Category "Menstrual" contains symptoms like
-- "heavy periods", "irregular cycles", "painful cramps"

CREATE TABLE IF NOT EXISTS symptom_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL,       -- e.g., "Menstrual", "Mental Health", "Pain"
    display_order INTEGER DEFAULT 0,          -- controls quiz display order
    icon TEXT                                 -- emoji or icon name for the UI
);

CREATE TABLE IF NOT EXISTS symptoms (
    symptom_id INTEGER PRIMARY KEY AUTOINCREMENT,
    symptom_name TEXT UNIQUE NOT NULL,        -- e.g., "Heavy periods"
    category_id INTEGER NOT NULL,
    description TEXT,                         -- brief explanation shown in quiz
    FOREIGN KEY (category_id) REFERENCES symptom_categories(category_id)
);


-- ============================================
-- 2. LIFE STAGES
-- ============================================
-- Users select their life stage in the quiz.
-- Stats are broken down by life stage so results feel personal.

CREATE TABLE IF NOT EXISTS life_stages (
    stage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    stage_name TEXT UNIQUE NOT NULL,          -- e.g., "Teens (13-17)"
    age_range_start INTEGER,
    age_range_end INTEGER,
    display_order INTEGER DEFAULT 0
);


-- ============================================
-- 3. ANONYMOUS QUIZ RESPONSES
-- ============================================
-- Each row = one person who took the quiz.
-- NO names, NO emails, NO identifying info. Ever.

CREATE TABLE IF NOT EXISTS responses (
    response_id INTEGER PRIMARY KEY AUTOINCREMENT,
    life_stage_id INTEGER NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (life_stage_id) REFERENCES life_stages(stage_id)
);

-- Which symptoms did this person select?
-- Many-to-many: one response can have many symptoms,
-- one symptom can appear in many responses.
CREATE TABLE IF NOT EXISTS response_symptoms (
    response_id INTEGER NOT NULL,
    symptom_id INTEGER NOT NULL,
    severity INTEGER DEFAULT 0,              -- 0=selected, 1=mild, 2=moderate, 3=severe
    PRIMARY KEY (response_id, symptom_id),
    FOREIGN KEY (response_id) REFERENCES responses(response_id),
    FOREIGN KEY (symptom_id) REFERENCES symptoms(symptom_id)
);


-- ============================================
-- 4. SYMPTOM CO-OCCURRENCES (pre-computed)
-- ============================================
-- Instead of computing "what % of women with symptom A
-- also have symptom B" on every page load, we pre-compute
-- it and store it. This is a common performance pattern.

CREATE TABLE IF NOT EXISTS symptom_cooccurrences (
    symptom_id_a INTEGER NOT NULL,
    symptom_id_b INTEGER NOT NULL,
    co_occurrence_count INTEGER DEFAULT 0,   -- how many people reported both
    co_occurrence_pct REAL DEFAULT 0,        -- percentage of A-reporters who also report B
    PRIMARY KEY (symptom_id_a, symptom_id_b),
    FOREIGN KEY (symptom_id_a) REFERENCES symptoms(symptom_id),
    FOREIGN KEY (symptom_id_b) REFERENCES symptoms(symptom_id)
);


-- ============================================
-- 5. SPECIALISTS
-- ============================================
-- Types of medical professionals, NOT specific doctors.

CREATE TABLE IF NOT EXISTS specialists (
    specialist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    specialist_type TEXT UNIQUE NOT NULL,     -- e.g., "Endocrinologist"
    description TEXT,                        -- what they do, in plain language
    what_to_expect TEXT,                     -- "At your first visit, expect..."
    icon TEXT                                -- emoji or icon for UI
);


-- ============================================
-- 6. SYMPTOM → SPECIALIST MAPPING
-- ============================================
-- Which symptom clusters point to which specialist?
-- A symptom can map to multiple specialists (e.g., fatigue
-- could mean endocrinologist OR therapist).

CREATE TABLE IF NOT EXISTS symptom_specialist_map (
    symptom_id INTEGER NOT NULL,
    specialist_id INTEGER NOT NULL,
    relevance_weight REAL DEFAULT 1.0,       -- higher = stronger match
    PRIMARY KEY (symptom_id, specialist_id),
    FOREIGN KEY (symptom_id) REFERENCES symptoms(symptom_id),
    FOREIGN KEY (specialist_id) REFERENCES specialists(specialist_id)
);


-- ============================================
-- 7. PUBMED RESEARCH ARTICLES
-- ============================================
-- Real research pulled from PubMed to back up our data.
-- Shown as "Learn more" links in the results.

CREATE TABLE IF NOT EXISTS articles (
    article_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pubmed_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    abstract TEXT,
    publication_date DATE,
    journal_name TEXT,
    doi TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Links articles to symptoms they're relevant to
CREATE TABLE IF NOT EXISTS article_symptoms (
    article_id INTEGER NOT NULL,
    symptom_id INTEGER NOT NULL,
    PRIMARY KEY (article_id, symptom_id),
    FOREIGN KEY (article_id) REFERENCES articles(article_id),
    FOREIGN KEY (symptom_id) REFERENCES symptoms(symptom_id)
);