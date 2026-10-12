-- ==============================================================================
-- ShopQ Enterprise Relational & DWDM Schema (PostgreSQL / Supabase)
-- ==============================================================================
-- Architecture Layers:
--  1. Identity Layer (Operational OLTP: canonical_product, canonical_variant,
--     retailer_listing, seller_offer)
--  2. Star Schema Dimensions (DWDM OLAP: dim_product, dim_variant, dim_retailer,
--     dim_seller, dim_category, dim_date)
--  3. Analytical Fact Tables (DWDM OLAP: fact_price_history, fact_recommendation,
--     fact_recommendation_outcome)
-- ==============================================================================

-- Enable common extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==============================================================================
-- UTILITY FUNCTIONS & TRIGGERS
-- ==============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- SECTION 1: STAR SCHEMA DIMENSIONS
-- Defined first so operational & analytical foreign keys can reference cleanly.
-- ==============================================================================

-- 1.1 dim_category (Conformed Category Dimension)
CREATE TABLE IF NOT EXISTS dim_category (
    category_key        BIGSERIAL PRIMARY KEY,
    category_id         VARCHAR(64) UNIQUE NOT NULL,
    category_name       VARCHAR(100) NOT NULL,
    parent_category_id  VARCHAR(64),
    parent_category_name VARCHAR(100),
    department          VARCHAR(100),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 1.2 dim_retailer (Conformed Retailer Dimension)
CREATE TABLE IF NOT EXISTS dim_retailer (
    retailer_key        BIGSERIAL PRIMARY KEY,
    retailer_id         VARCHAR(64) UNIQUE NOT NULL,
    retailer_name       VARCHAR(150) NOT NULL,
    domain_url          VARCHAR(255),
    country             VARCHAR(10) NOT NULL DEFAULT 'IN',
    currency_code       VARCHAR(10) NOT NULL DEFAULT 'INR',
    reliability_score   NUMERIC(4, 2) NOT NULL DEFAULT 0.95,
    is_verified         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 1.3 dim_seller (Conformed Seller Dimension)
CREATE TABLE IF NOT EXISTS dim_seller (
    seller_key          BIGSERIAL PRIMARY KEY,
    seller_id           VARCHAR(64) UNIQUE NOT NULL,
    seller_name         VARCHAR(255) NOT NULL,
    rating              NUMERIC(3, 2),
    review_count        INTEGER NOT NULL DEFAULT 0,
    reliability_tier    VARCHAR(50) NOT NULL DEFAULT 'RELIABLE', -- 'RELIABLE', 'MODERATE', 'RISKY', 'UNKNOWN'
    return_policy       VARCHAR(255),
    warranty_terms      VARCHAR(255),
    is_authorized       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 1.4 dim_date (Conformed Date Dimension for Time-Series DWDM Analysis)
CREATE TABLE IF NOT EXISTS dim_date (
    date_key            INTEGER PRIMARY KEY, -- Format: YYYYMMDD (e.g. 20261007)
    full_date           DATE UNIQUE NOT NULL,
    day_of_week         SMALLINT NOT NULL,   -- 1 = Monday, 7 = Sunday (ISO)
    day_name            VARCHAR(15) NOT NULL,
    day_of_month        SMALLINT NOT NULL,
    day_of_year         SMALLINT NOT NULL,
    week_of_year        SMALLINT NOT NULL,
    month_number        SMALLINT NOT NULL,
    month_name          VARCHAR(15) NOT NULL,
    quarter             SMALLINT NOT NULL,
    year_number         INTEGER NOT NULL,
    is_weekend          BOOLEAN NOT NULL DEFAULT FALSE,
    is_holiday          BOOLEAN NOT NULL DEFAULT FALSE,
    fiscal_year         INTEGER NOT NULL,
    fiscal_quarter      SMALLINT NOT NULL
);

-- ==============================================================================
-- SECTION 2: IDENTITY LAYER TABLES (4-Level Product Identity)
-- ==============================================================================

-- 2.1 canonical_product
-- Represents the global, normalized brand & product catalog entity.
CREATE TABLE IF NOT EXISTS canonical_product (
    id                  VARCHAR(64) PRIMARY KEY,
    brand               VARCHAR(100) NOT NULL,
    canonical_name      VARCHAR(255) NOT NULL,
    category_id         VARCHAR(64) NOT NULL REFERENCES dim_category(category_id) ON UPDATE CASCADE,
    canonical_image_url TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_canonical_product_updated_at
BEFORE UPDATE ON canonical_product
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 2.2 canonical_variant
-- Specific SKU/Model variation under a canonical product (Color, Storage, Size, etc.)
CREATE TABLE IF NOT EXISTS canonical_variant (
    id                  VARCHAR(64) PRIMARY KEY,
    product_id          VARCHAR(64) NOT NULL REFERENCES canonical_product(id) ON DELETE CASCADE,
    model_number        VARCHAR(100),
    variant_name        VARCHAR(255) NOT NULL,
    storage             VARCHAR(50),
    color               VARCHAR(50),
    size                VARCHAR(50),
    attributes_json     JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_canonical_variant_updated_at
BEFORE UPDATE ON canonical_variant
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 2.3 retailer_listing
-- Retailer-specific product page URL & metadata pointing to a canonical variant.
CREATE TABLE IF NOT EXISTS retailer_listing (
    id                  VARCHAR(64) PRIMARY KEY,
    variant_id          VARCHAR(64) NOT NULL REFERENCES canonical_variant(id) ON DELETE CASCADE,
    retailer_id         VARCHAR(64) NOT NULL REFERENCES dim_retailer(retailer_id) ON UPDATE CASCADE,
    external_product_id VARCHAR(255),
    title               VARCHAR(500) NOT NULL,
    product_url         TEXT NOT NULL,
    image_url           TEXT,
    first_seen_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at        TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status              VARCHAR(50) NOT NULL DEFAULT 'ACTIVE' -- 'ACTIVE', 'INACTIVE', 'OUT_OF_STOCK', 'DISCONTINUED'
);

-- 2.4 seller_offer
-- Point-in-time merchant/seller quote on a retailer listing (price, stock, warranty).
CREATE TABLE IF NOT EXISTS seller_offer (
    id                  VARCHAR(64) PRIMARY KEY,
    listing_id          VARCHAR(64) NOT NULL REFERENCES retailer_listing(id) ON DELETE CASCADE,
    seller_id           VARCHAR(64) NOT NULL REFERENCES dim_seller(seller_id) ON UPDATE CASCADE,
    price               NUMERIC(12, 2) NOT NULL CHECK (price >= 0),
    shipping_cost       NUMERIC(12, 2) NOT NULL DEFAULT 0.00 CHECK (shipping_cost >= 0),
    discount            NUMERIC(12, 2) NOT NULL DEFAULT 0.00 CHECK (discount >= 0),
    currency            VARCHAR(10) NOT NULL DEFAULT 'INR',
    availability        VARCHAR(50) NOT NULL DEFAULT 'IN_STOCK', -- 'IN_STOCK', 'OUT_OF_STOCK', 'PRE_ORDER', 'LIMITED_STOCK'
    observed_at         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    collected_at        TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_type         VARCHAR(50) NOT NULL DEFAULT 'SCRAPER' -- 'SCRAPER', 'API', 'FEED', 'EXTENSION'
);

-- ==============================================================================
-- SECTION 3: PRODUCT & VARIANT DIMENSIONS (Synchronized DW Dimensions)
-- ==============================================================================

-- 3.1 dim_product (Dimensional Representation of canonical_product)
CREATE TABLE IF NOT EXISTS dim_product (
    product_key         BIGSERIAL PRIMARY KEY,
    product_id          VARCHAR(64) UNIQUE NOT NULL REFERENCES canonical_product(id) ON DELETE CASCADE,
    brand               VARCHAR(100) NOT NULL,
    canonical_name      VARCHAR(255) NOT NULL,
    category_id         VARCHAR(64) REFERENCES dim_category(category_id) ON UPDATE CASCADE,
    category_name       VARCHAR(100),
    canonical_image_url TEXT,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_dim_product_updated_at
BEFORE UPDATE ON dim_product
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 3.2 dim_variant (Dimensional Representation of canonical_variant)
CREATE TABLE IF NOT EXISTS dim_variant (
    variant_key         BIGSERIAL PRIMARY KEY,
    variant_id          VARCHAR(64) UNIQUE NOT NULL REFERENCES canonical_variant(id) ON DELETE CASCADE,
    product_id          VARCHAR(64) NOT NULL REFERENCES canonical_product(id) ON DELETE CASCADE,
    model_number        VARCHAR(100),
    variant_name        VARCHAR(255) NOT NULL,
    storage             VARCHAR(50),
    color               VARCHAR(50),
    size                VARCHAR(50),
    attributes_json     JSONB DEFAULT '{}'::jsonb,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================================
-- SECTION 4: ANALYTICAL FACT TABLES (DWDM)
-- ==============================================================================

-- 4.1 fact_price_history
-- Granular time-series price, stock, and source observation facts.
CREATE TABLE IF NOT EXISTS fact_price_history (
    price_observation_id BIGSERIAL PRIMARY KEY,
    variant_id          VARCHAR(64) NOT NULL REFERENCES canonical_variant(id) ON DELETE CASCADE,
    retailer_id         VARCHAR(64) NOT NULL REFERENCES dim_retailer(retailer_id) ON UPDATE CASCADE,
    seller_id           VARCHAR(64) NOT NULL REFERENCES dim_seller(seller_id) ON UPDATE CASCADE,
    observed_at         TIMESTAMPTZ NOT NULL,
    collected_at        TIMESTAMPTZ NOT NULL,
    price               NUMERIC(12, 2) NOT NULL CHECK (price >= 0),
    currency            VARCHAR(10) NOT NULL DEFAULT 'INR',
    shipping_cost       NUMERIC(12, 2) NOT NULL DEFAULT 0.00 CHECK (shipping_cost >= 0),
    discount            NUMERIC(12, 2) NOT NULL DEFAULT 0.00 CHECK (discount >= 0),
    in_stock            BOOLEAN NOT NULL DEFAULT TRUE,
    availability_status VARCHAR(50) NOT NULL DEFAULT 'IN_STOCK',
    source_url          TEXT,
    source_type         VARCHAR(50) NOT NULL DEFAULT 'SCRAPER',
    -- Conformed DW Star Schema Keys
    date_key            INTEGER REFERENCES dim_date(date_key),
    variant_key         BIGINT REFERENCES dim_variant(variant_key),
    retailer_key        BIGINT REFERENCES dim_retailer(retailer_key),
    seller_key          BIGINT REFERENCES dim_seller(seller_key)
);

-- 4.2 fact_recommendation
-- Snapshots of algorithmic price recommendation decisions and confidence scores.
CREATE TABLE IF NOT EXISTS fact_recommendation (
    recommendation_id      VARCHAR(64) PRIMARY KEY,
    product_id             VARCHAR(64) NOT NULL REFERENCES canonical_product(id) ON DELETE CASCADE,
    timestamp              TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    decision               VARCHAR(50) NOT NULL, -- 'BUY', 'WAIT', 'CAUTION', 'CHECK_ALT', 'YOUR_CALL', 'NO_DECISION'
    buy_point              NUMERIC(12, 2),
    model_version          VARCHAR(50) NOT NULL,
    matching_model_version VARCHAR(50),
    decision_rules_version VARCHAR(50),
    confidence_level       VARCHAR(50) NOT NULL, -- 'HIGH', 'MEDIUM', 'LOW'
    current_price          NUMERIC(12, 2) NOT NULL,
    predicted_direction    VARCHAR(50),          -- 'FALLING', 'RISING', 'STABLE', 'VOLATILE'
    primary_reason         TEXT NOT NULL,
    data_freshness         VARCHAR(50),          -- e.g. '3 mins ago'
    data_coverage          NUMERIC(5, 2),        -- e.g. 0.95 (95% data coverage)
    -- Conformed DW Star Schema Keys
    date_key               INTEGER REFERENCES dim_date(date_key),
    product_key            BIGINT REFERENCES dim_product(product_key)
);

-- 4.3 fact_recommendation_outcome
-- Evaluation of prediction accuracy vs future realized prices.
CREATE TABLE IF NOT EXISTS fact_recommendation_outcome (
    outcome_id            BIGSERIAL PRIMARY KEY,
    recommendation_id     VARCHAR(64) NOT NULL REFERENCES fact_recommendation(recommendation_id) ON DELETE CASCADE,
    observed_future_price NUMERIC(12, 2),
    outcome_status        VARCHAR(50) NOT NULL, -- 'ACCURATE', 'MISSED_OPPORTUNITY', 'FALSE_ALARM', 'PENDING_EVALUATION', 'VALIDATED'
    evaluated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================================
-- SECTION 5: HELPER DATE POPULATION STORED PROCEDURE
-- Utility to generate dim_date records between any start and end date.
-- ==============================================================================

CREATE OR REPLACE FUNCTION populate_dim_date(p_start_date DATE, p_end_date DATE)
RETURNS VOID AS $$
DECLARE
    curr_date DATE := p_start_date;
BEGIN
    WHILE curr_date <= p_end_date LOOP
        INSERT INTO dim_date (
            date_key,
            full_date,
            day_of_week,
            day_name,
            day_of_month,
            day_of_year,
            week_of_year,
            month_number,
            month_name,
            quarter,
            year_number,
            is_weekend,
            is_holiday,
            fiscal_year,
            fiscal_quarter
        )
        VALUES (
            CAST(TO_CHAR(curr_date, 'YYYYMMDD') AS INTEGER),
            curr_date,
            EXTRACT(ISODOW FROM curr_date)::SMALLINT,
            TO_CHAR(curr_date, 'FMDay'),
            EXTRACT(DAY FROM curr_date)::SMALLINT,
            EXTRACT(DOY FROM curr_date)::SMALLINT,
            EXTRACT(WEEK FROM curr_date)::SMALLINT,
            EXTRACT(MONTH FROM curr_date)::SMALLINT,
            TO_CHAR(curr_date, 'FMMonth'),
            EXTRACT(QUARTER FROM curr_date)::SMALLINT,
            EXTRACT(YEAR FROM curr_date)::INTEGER,
            CASE WHEN EXTRACT(ISODOW FROM curr_date) IN (6, 7) THEN TRUE ELSE FALSE END,
            FALSE,
            EXTRACT(YEAR FROM curr_date)::INTEGER,
            EXTRACT(QUARTER FROM curr_date)::SMALLINT
        )
        ON CONFLICT (date_key) DO NOTHING;

        curr_date := curr_date + INTERVAL '1 day';
    END LOOP;
END;
$$ LANGUAGE plpgsql;
