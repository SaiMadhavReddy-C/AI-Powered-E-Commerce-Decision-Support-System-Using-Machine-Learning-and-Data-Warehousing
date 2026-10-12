-- ==============================================================================
-- ShopQ Performance Tuning & Indexing Script (PostgreSQL / Supabase)
-- ==============================================================================
-- Indexes optimized for:
--  - Sub-millisecond operational lookups
--  - High-throughput price scraping ingestion
--  - Time-series sliding window analytical aggregations (7d/30d/90d)
--  - Multi-retailer & multi-seller price comparisons
-- ==============================================================================

-- ==============================================================================
-- 1. MANDATORY ANALYTICAL COMPOSITE INDEXES ON fact_price_history
-- ==============================================================================

-- Index 1: variant_id + observed_at
-- Crucial for rendering 30-day/90-day price trend charts for a specific variant
CREATE INDEX IF NOT EXISTS idx_fact_price_history_variant_observed
ON fact_price_history (variant_id, observed_at DESC);

-- Index 2: retailer_id + observed_at
-- Crucial for monitoring retailer price movements, scrape frequency, and retailer analytics
CREATE INDEX IF NOT EXISTS idx_fact_price_history_retailer_observed
ON fact_price_history (retailer_id, observed_at DESC);

-- Index 3: seller_id + observed_at
-- Crucial for auditing seller pricing behaviors, margin trends, and anomaly detection
CREATE INDEX IF NOT EXISTS idx_fact_price_history_seller_observed
ON fact_price_history (seller_id, observed_at DESC);

-- ==============================================================================
-- 2. ADDITIONAL HIGH-PERFORMANCE INDEXES ON fact_price_history
-- ==============================================================================

-- Fast cross-retailer comparison for a specific variant at a given point in time
CREATE INDEX IF NOT EXISTS idx_fact_price_history_variant_retailer_observed
ON fact_price_history (variant_id, retailer_id, observed_at DESC);

-- Covering index for finding 90-day lowest price (historicalLow computation)
CREATE INDEX IF NOT EXISTS idx_fact_price_history_variant_price
ON fact_price_history (variant_id, price ASC, observed_at DESC);

-- Star Schema foreign key join indexes
CREATE INDEX IF NOT EXISTS idx_fact_price_history_date_key
ON fact_price_history (date_key);

CREATE INDEX IF NOT EXISTS idx_fact_price_history_variant_key
ON fact_price_history (variant_key);

CREATE INDEX IF NOT EXISTS idx_fact_price_history_retailer_key
ON fact_price_history (retailer_key);

CREATE INDEX IF NOT EXISTS idx_fact_price_history_seller_key
ON fact_price_history (seller_key);

-- Partial index for fast filtering of out-of-stock events
CREATE INDEX IF NOT EXISTS idx_fact_price_history_oos
ON fact_price_history (variant_id, observed_at DESC)
WHERE in_stock = FALSE OR availability_status = 'OUT_OF_STOCK';

-- ==============================================================================
-- 3. IDENTITY LAYER OPERATIONAL INDEXES
-- ==============================================================================

-- canonical_product indexes
CREATE INDEX IF NOT EXISTS idx_canonical_product_brand
ON canonical_product (brand);

CREATE INDEX IF NOT EXISTS idx_canonical_product_category
ON canonical_product (category_id);

CREATE INDEX IF NOT EXISTS idx_canonical_product_canonical_name_trgm
ON canonical_product (canonical_name);

-- canonical_variant indexes
CREATE INDEX IF NOT EXISTS idx_canonical_variant_product_id
ON canonical_variant (product_id);

CREATE INDEX IF NOT EXISTS idx_canonical_variant_model_number
ON canonical_variant (model_number);

-- GIN index for querying flexible attribute parameters (e.g. noise_cancelling, wattage, connectivity)
CREATE INDEX IF NOT EXISTS idx_canonical_variant_attributes_gin
ON canonical_variant USING gin (attributes_json);

-- retailer_listing indexes
CREATE INDEX IF NOT EXISTS idx_retailer_listing_variant_id
ON retailer_listing (variant_id);

CREATE INDEX IF NOT EXISTS idx_retailer_listing_retailer_id
ON retailer_listing (retailer_id);

CREATE INDEX IF NOT EXISTS idx_retailer_listing_external_id
ON retailer_listing (retailer_id, external_product_id);

CREATE INDEX IF NOT EXISTS idx_retailer_listing_active_status
ON retailer_listing (variant_id, retailer_id)
WHERE status = 'ACTIVE';

-- seller_offer indexes
CREATE INDEX IF NOT EXISTS idx_seller_offer_listing_observed
ON seller_offer (listing_id, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_seller_offer_seller_observed
ON seller_offer (seller_id, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_seller_offer_price
ON seller_offer (price ASC);

-- ==============================================================================
-- 4. ANALYTICAL RECOMMENDATION FACTS INDEXES
-- ==============================================================================

-- Fast retrieval of latest recommendation decision per product
CREATE INDEX IF NOT EXISTS idx_fact_recommendation_product_ts
ON fact_recommendation (product_id, timestamp DESC);

-- Analytical filtering by recommendation decision (BUY, WAIT, CAUTION, etc.)
CREATE INDEX IF NOT EXISTS idx_fact_recommendation_decision
ON fact_recommendation (decision, confidence_level);

-- Recommendation tracking by date_key and model version for A/B testing
CREATE INDEX IF NOT EXISTS idx_fact_recommendation_model_date
ON fact_recommendation (model_version, date_key);

-- Outcome accuracy evaluation joins
CREATE INDEX IF NOT EXISTS idx_fact_recommendation_outcome_rec
ON fact_recommendation_outcome (recommendation_id);

CREATE INDEX IF NOT EXISTS idx_fact_recommendation_outcome_status
ON fact_recommendation_outcome (outcome_status, evaluated_at DESC);

-- ==============================================================================
-- 5. STAR SCHEMA DIMENSIONS LOOKUP INDEXES
-- ==============================================================================

CREATE INDEX IF NOT EXISTS idx_dim_category_parent
ON dim_category (parent_category_id);

CREATE INDEX IF NOT EXISTS idx_dim_product_category
ON dim_product (category_id);

CREATE INDEX IF NOT EXISTS idx_dim_variant_product
ON dim_variant (product_id);

CREATE INDEX IF NOT EXISTS idx_dim_seller_reliability
ON dim_seller (reliability_tier, rating DESC);

CREATE INDEX IF NOT EXISTS idx_dim_date_full_date
ON dim_date (full_date);

CREATE INDEX IF NOT EXISTS idx_dim_date_year_month
ON dim_date (year_number, month_number);
