# ShopQ Database & DWDM Architecture (PostgreSQL / Supabase)

This directory contains the production-grade PostgreSQL / Supabase schema, indexing strategies, and seed fixtures for **ShopQ**, an intelligent price tracking and deal-recommendation platform.

---

## 1. Architectural Overview

ShopQ separates transactional ingestion from dimensional analytics via a hybrid Operational & DWDM (Data Warehousing and Data Mining) design:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   IDENTITY LAYER (Operational OLTP)                   │
│                                                                        │
│   canonical_product ──1:N──> canonical_variant                        │
│                                      │                                 │
│                                     1:N                                │
│                                      ▼                                 │
│                               retailer_listing ──1:N──> seller_offer  │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                         ETL / Continuous Feed
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   STAR SCHEMA (Analytical OLAP / DWDM)                 │
│                                                                        │
│      dim_date          dim_retailer      dim_seller      dim_variant   │
│         │                   │                │                │        │
│         └───────────┬───────┴────────┬───────┴────────┬───────┘        │
│                     ▼                ▼                ▼                │
│              fact_price_history   fact_recommendation                  │
│                                              │                         │
│                                             1:N                        │
│                                              ▼                         │
│                                 fact_recommendation_outcome            │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Directory Structure

- `schema.sql`: Complete DDL definitions for Identity Layer tables, Star Schema Dimensions, Analytical Fact Tables, constraints, and helper functions (including `populate_dim_date`).
- `indexes.sql`: High-performance B-tree, GIN, and partial index definitions for sub-millisecond retrieval, sliding-window price history lookups, and scrape ingest pipelines.
- `seed.sql`: Realistic seed fixtures covering all 12 core ShopQ demo scenarios (Sony WH-1000XM5, iPhone 15, boAt Airdopes, PS5 Pro, Nike Air Max, etc.).

---

## 3. Schema Specifications

### 3.1 Identity Layer (4-Level Product Model)
1. **`canonical_product`**: Master brand and product catalog definition.
   - `id`, `brand`, `canonical_name`, `category_id`, `canonical_image_url`, `created_at`, `updated_at`.
2. **`canonical_variant`**: Specific SKU/model variants (storage, color, size, specification JSON).
   - `id`, `product_id`, `model_number`, `variant_name`, `storage`, `color`, `size`, `attributes_json`, `created_at`, `updated_at`.
3. **`retailer_listing`**: Retailer-specific product landing pages mapped to canonical variants.
   - `id`, `variant_id`, `retailer_id`, `external_product_id`, `title`, `product_url`, `image_url`, `first_seen_at`, `last_seen_at`, `status`.
4. **`seller_offer`**: Granular merchant quotes on retailer listings.
   - `id`, `listing_id`, `seller_id`, `price`, `shipping_cost`, `discount`, `currency`, `availability`, `observed_at`, `collected_at`, `source_type`.

### 3.2 Conformed Star Schema Dimensions
1. **`dim_category`**: Hierarchy attributes (`category_id`, `category_name`, `parent_category_name`, `department`).
2. **`dim_product`**: Product dimension with brand and active status flags.
3. **`dim_variant`**: SKU dimension with normalized physical and technical attributes.
4. **`dim_retailer`**: Marketplace and platform dimension with reliability ratings and domain URLs.
5. **`dim_seller`**: Merchant dimension with merchant tiering (`RELIABLE`, `MODERATE`, `RISKY`), ratings, and warranty guarantees.
6. **`dim_date`**: Kimball standard calendar dimension supporting day-of-week, quarter, and fiscal breakdowns.

### 3.3 Analytical Fact Tables
1. **`fact_price_history`**: High-frequency price observation log.
   - Primary key: `price_observation_id`
   - Core keys & metrics: `variant_id`, `retailer_id`, `seller_id`, `observed_at`, `collected_at`, `price`, `currency`, `shipping_cost`, `discount`, `in_stock`, `availability_status`, `source_url`, `source_type`.
   - Dimension FKs: `date_key`, `variant_key`, `retailer_key`, `seller_key`.
2. **`fact_recommendation`**: Decision audit snapshots produced by ShopQ's recommendation engine.
   - Keys & metrics: `recommendation_id`, `product_id`, `timestamp`, `decision` (`BUY`, `WAIT`, `CAUTION`, `CHECK_ALT`, `YOUR_CALL`, `NO_DECISION`), `buy_point`, `model_version`, `matching_model_version`, `decision_rules_version`, `confidence_level`, `current_price`, `predicted_direction`, `primary_reason`, `data_freshness`, `data_coverage`.
3. **`fact_recommendation_outcome`**: Evaluation facts closing the feedback loop between predictions and subsequent price realization.
   - Keys: `outcome_id`, `recommendation_id`, `observed_future_price`, `outcome_status` (`ACCURATE`, `MISSED_OPPORTUNITY`, `FALSE_ALARM`, `VALIDATED`, `PENDING_EVALUATION`), `evaluated_at`.

---

## 4. Indexing & Performance Strategy

The database includes indexes tailored for query access patterns:
- **Variant Time Series**: `fact_price_history(variant_id, observed_at DESC)` ensures 30d/90d price chart generation without table scans.
- **Retailer Auditing**: `fact_price_history(retailer_id, observed_at DESC)` supports retailer scrape freshness and rate-limit tracking.
- **Seller Margin Audits**: `fact_price_history(seller_id, observed_at DESC)` tracks merchant repricing behavior.
- **Attribute Queries**: `canonical_variant USING gin (attributes_json)` allows arbitrary feature filtering (ANC, wattage, RAM, display).
- **Out of Stock Partitions**: Partial index `WHERE in_stock = FALSE OR availability_status = 'OUT_OF_STOCK'`.

---

## 5. Execution & Migration Guide

To run on a local PostgreSQL instance or Supabase SQL Editor:

```bash
# 1. Apply Schema
psql -h <host> -U <user> -d <database> -f schema.sql

# 2. Apply Indexes
psql -h <host> -U <user> -d <database> -f indexes.sql

# 3. Apply Demo Seeds
psql -h <host> -U <user> -d <database> -f seed.sql
```
