-- =============================================================================
-- UMLS Metathesaurus — Optimized PostgreSQL schema for Entity Linking
-- FIXED VERSION (PostgreSQL + UMLS RRF compatible)
-- =============================================================================

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

-- =============================================================================
-- MRCONSO
-- =============================================================================
DROP TABLE IF EXISTS MRCONSO CASCADE;

CREATE TABLE MRCONSO (
    CUI char(8) NOT NULL,
    LAT char(3) NOT NULL,
    TS char(1) NOT NULL,
    LUI varchar(10) NOT NULL,
    STT varchar(3) NOT NULL,
    SUI varchar(10) NOT NULL,
    ISPREF char(1) NOT NULL,
    AUI varchar(9) NOT NULL,
    SAUI varchar(50),
    SCUI varchar(100),
    SDUI varchar(100),
    SAB varchar(40) NOT NULL,
    TTY varchar(40) NOT NULL,
    CODE varchar(100) NOT NULL,
    STR text NOT NULL,
    SRL integer NOT NULL,
    SUPPRESS char(1) NOT NULL,
    CVF integer,
    DUMMY text
);

\copy MRCONSO FROM 'MRCONSO.RRF' WITH (FORMAT csv, DELIMITER '|', NULL '');

DELETE FROM MRCONSO WHERE SUPPRESS <> 'N';

DELETE FROM MRCONSO
WHERE LAT NOT IN ('ENG','SPA','FRE','GER','ITA','POR','DUT','SWE','NOR','DAN','FIN','POL','CZE','HUN','BAQ','LAV','EST');

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX idx_mrconso_cui ON MRCONSO (CUI);
CREATE INDEX idx_mrconso_sab ON MRCONSO (SAB);

-- FAST fuzzy search (main candidate retrieval)
CREATE INDEX idx_mrconso_str_trgm
ON MRCONSO USING GIN (STR gin_trgm_ops);

-- Full-text search
CREATE INDEX idx_mrconso_str_fts
ON MRCONSO
USING GIN (to_tsvector('simple', left(STR, 50000)));

-- Preferred English concepts
CREATE INDEX idx_mrconso_pref_eng
ON MRCONSO (CUI)
WHERE LAT='ENG' AND TS='P';

-- =============================================================================
-- MRSTY
-- =============================================================================
DROP TABLE IF EXISTS MRSTY CASCADE;

CREATE TABLE MRSTY (
    CUI char(8) NOT NULL,
    TUI char(4) NOT NULL,
    STN varchar(100) NOT NULL,
    STY varchar(50) NOT NULL,
    ATUI varchar(11) NOT NULL,
    CVF integer,
    DUMMY text
);

\copy MRSTY FROM 'MRSTY.RRF' WITH (FORMAT csv, DELIMITER '|', NULL '');

CREATE INDEX idx_mrsty_cui ON MRSTY (CUI);
CREATE INDEX idx_mrsty_tui ON MRSTY (TUI);
CREATE INDEX idx_mrsty_sty ON MRSTY (STY);

-- =============================================================================
-- MRDEF
-- =============================================================================
DROP TABLE IF EXISTS MRDEF CASCADE;

CREATE TABLE MRDEF (
    CUI char(8) NOT NULL,
    AUI varchar(9) NOT NULL,
    ATUI varchar(11) NOT NULL,
    SATUI varchar(50),
    SAB varchar(40) NOT NULL,
    DEF text NOT NULL,
    SUPPRESS char(1) NOT NULL,
    CVF integer,
    DUMMY text
);

\copy MRDEF FROM 'MRDEF.RRF' WITH (FORMAT csv, DELIMITER '|', NULL '');

DELETE FROM MRDEF WHERE SUPPRESS <> 'N';

CREATE INDEX idx_mrdef_cui ON MRDEF (CUI);
CREATE INDEX idx_mrdef_def_fts
ON MRDEF USING GIN (to_tsvector('simple', DEF));

-- =============================================================================
-- MRREL
-- =============================================================================
DROP TABLE IF EXISTS MRREL CASCADE;

CREATE TABLE MRREL (
    CUI1 char(8) NOT NULL,
    AUI1 varchar(9),
    STYPE1 varchar(50) NOT NULL,
    REL varchar(4) NOT NULL,
    CUI2 char(8) NOT NULL,
    AUI2 varchar(9),
    STYPE2 varchar(50) NOT NULL,
    RELA varchar(100),
    RUI varchar(10) NOT NULL,
    SRUI varchar(50),
    SAB varchar(40) NOT NULL,
    SL varchar(40) NOT NULL,
    RG varchar(10),
    DIR varchar(1),
    SUPPRESS char(1) NOT NULL,
    CVF integer,
    DUMMY text
);

\copy MRREL FROM 'MRREL.RRF' WITH (FORMAT csv, DELIMITER '|', NULL '');

DELETE FROM MRREL WHERE SUPPRESS <> 'N';

CREATE INDEX idx_mrrel_cui1 ON MRREL (CUI1);
CREATE INDEX idx_mrrel_cui2 ON MRREL (CUI2);
CREATE INDEX idx_mrrel_rel ON MRREL (REL);
CREATE INDEX idx_mrrel_cui1_rel ON MRREL (CUI1, REL);

-- =============================================================================
-- ANALYZE (IMPORTANT)
-- =============================================================================
ANALYZE MRCONSO;
ANALYZE MRSTY;
ANALYZE MRDEF;
ANALYZE MRREL;