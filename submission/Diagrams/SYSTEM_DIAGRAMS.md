# ShopQ Architecture & System Diagrams
## Technical Diagram Suite for Academic Submission

This document contains 10 formal system architecture diagrams rendered using standard Mermaid markdown syntax.

---

### 1. Use Case Diagram

Visualizes user interactions with the Web Application and Chrome Extension across core decision workflows.

```mermaid
graph TD
    User((Shopper / User))

    subgraph ShopQ Platform
        UC1[Search Product Query]
        UC2[Paste Retailer URL]
        UC3[View Price Analysis & Decision]
        UC4[Inspect 'Why' Explanations & Gates]
        UC5[Compare Cross-Retailer Prices]
        UC6[Add Item to Watchlist]
        UC7[Configure Price Alerts & Preferences]
        UC8[View Decision in Chrome Side Panel]
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC7
    User --> UC8
```

---

### 2. System Architecture Diagram

Depicts the end-to-end multi-tier architecture connecting clients, FastAPI backend modules, ScraperAPI proxy, ML engine, and Supabase DWDM.

```mermaid
graph TB
    subgraph Client Layer
        Web[Vite + React Web App\n#FAF8F5 / #C96B7A]
        Ext[Chrome Extension MV3\nSide Panel & Shadow DOM]
    end

    subgraph API & Gateway Layer
        FastAPI[FastAPI Backend Gateway\napp/main.py]
        Security[Security Core\nSSRF, CORS, Sanitizer]
        Registry[Provider Registry\nprovider_registry.py]
    end

    subgraph Data Acquisition Layer
        ScraperAPI[ScraperAPI Proxy Gateway\nIndia Geotargeting & JS Render]
        Retailers[(10 Indian Retailers\nAmazon, Flipkart, Croma...)]
    end

    subgraph Intelligence Layer
        ML[PriceTrend-v2 Model\nTier 1/2/3 Prediction]
        Gates[Hard BUY Safety Gates\n7 Mandatory Checks]
        Synth[Decision Synthesizer\nsynthesizer.py]
    end

    subgraph Persistence Layer DWDM
        Supabase[(Supabase PostgreSQL\nOLTP & Star Schema)]
    end

    Web -->|HTTP REST| FastAPI
    Ext -->|HTTP REST| FastAPI
    FastAPI --> Security
    FastAPI --> Registry
    Registry -->|Proxy Request| ScraperAPI
    ScraperAPI -->|Scrape DOM| Retailers
    FastAPI --> ML
    FastAPI --> Gates
    Gates --> Synth
    ML --> Synth
    FastAPI -->|Fact & Dim Writes| Supabase
```

---

### 3. Data Flow Diagram — Level 0 (Context Level DFD)

High-level boundary representation of inputs and outputs between external entities and the ShopQ System.

```mermaid
graph LR
    User((Shopper))
    Retailer((Retailer Websites))
    
    subgraph ShopQ System
        System[ShopQ Core Engine\nProcess 0.0]
    end

    User -->|1. Product Query or URL| System
    System -->|2. ScraperAPI Proxy Fetch| Retailer
    Retailer -->|3. Scraped DOM / HTML| System
    System -->|4. Structured Decision JSON| User
```

---

### 4. Data Flow Diagram — Level 1 (Decomposed Sub-processes DFD)

Decomposes the internal processing steps: Capture, Extraction, Resolution, Persistence, Analysis, Decision Synthesis.

```mermaid
graph TD
    User((Shopper))
    Retailers((Retailer Sites))

    subgraph Processes
        P1[1.0 Capture & SSRF Validate]
        P2[2.0 ScraperAPI Extraction]
        P3[3.0 Clean & Canonicalize]
        P4[4.0 DWDM ETL Persistence]
        P5[5.0 ML Trend Prediction]
        P6[6.0 Safety Gate & Decision Synthesis]
    end

    subgraph Data Stores
        D1[(OLTP Identity Catalog)]
        D2[(DWDM Star Schema)]
    end

    User -->|URL / Search| P1
    P1 -->|Validated URL| P2
    P2 -->|HTTP Request| Retailers
    Retailers -->|DOM Payload| P2
    P2 -->|Raw Data| P3
    P3 -->|Resolved SKU| D1
    P3 -->|Curated Offer| P4
    P4 -->|Fact Record| D2
    D2 -->|Time Series History| P5
    P5 -->|Price Forecast| P6
    P3 -->|Product & Seller Metrics| P6
    P6 -->|Final Decision JSON| User
```

---

### 5. Entity-Relationship (ER) Diagram — Operational Identity Layer

Shows the 4-level product identity hierarchy: `canonical_product` $\rightarrow$ `canonical_variant` $\rightarrow$ `retailer_listing` $\rightarrow$ `seller_offer`.

```mermaid
erDiagram
    CANONICAL_PRODUCT ||--|{ CANONICAL_VARIANT : contains
    CANONICAL_VARIANT ||--|{ RETAILER_LISTING : lists_on
    RETAILER_LISTING ||--|{ SELLER_OFFER : quoted_by
    DIM_RETAILER ||--|{ RETAILER_LISTING : operates
    DIM_SELLER ||--|{ SELLER_OFFER : provides

    CANONICAL_PRODUCT {
        string id PK
        string brand
        string canonical_name
        string category_id FK
    }

    CANONICAL_VARIANT {
        string id PK
        string product_id FK
        string model_number
        string variant_name
        string storage
        string color
    }

    RETAILER_LISTING {
        string id PK
        string variant_id FK
        string retailer_id FK
        string title
        string product_url
    }

    SELLER_OFFER {
        string id PK
        string listing_id FK
        string seller_id FK
        decimal price
        decimal shipping_cost
        string availability
        timestamp observed_at
    }
```

---

### 6. Class Diagram — Backend Services & Decision Architecture

Class structure of services involved in request processing, ML prediction, safety gating, and decision synthesis.

```mermaid
classDiagram
    class ProviderRegistry {
        +get_provider(url: str) BaseProvider
        +extract(url: str) ScrapedOffer
    }

    class ScraperAPIProvider {
        +api_key: str
        +fetch_dom(url: str) str
        +parse_offer(html: str) ScrapedOffer
    }

    class HardBuySafetyGate {
        +evaluate(product: ProductDetail) SafetyGateResult
        -_check_product_match() GateEval
        -_check_exact_variant() GateEval
        -_check_fresh_data() GateEval
        -_check_acceptable_seller() GateEval
        -_check_in_stock() GateEval
        -_check_trusted_source() GateEval
        -_check_sufficient_coverage() GateEval
    }

    class PricePredictor {
        +model_tier: str
        +predict(history: List, current_price: float) PricePredictionResult
    }

    class ConfidenceEngine {
        +evaluate(product: ProductDetail) ConfidenceReport
    }

    class DecisionSynthesizer {
        +synthesize(product: ProductDetail) DecisionSchema
    }

    ProviderRegistry --> ScraperAPIProvider
    DecisionSynthesizer --> HardBuySafetyGate
    DecisionSynthesizer --> PricePredictor
    DecisionSynthesizer --> ConfidenceEngine
```

---

### 7. Sequence Diagram — Product Analysis Flow

Triggers when a user clicks analyze or inputs a URL.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as React / Extension
    participant API as FastAPI Backend
    participant Security as Security Core
    participant Registry as Provider Registry
    participant Scraper as ScraperAPI
    participant DB as Supabase DWDM
    participant Gate as Hard BUY Gate
    participant ML as PriceTrend-v2 ML
    participant Synth as Synthesizer

    User->>Frontend: Request Analysis (URL / Product ID)
    Frontend->>API: POST /api/analyze { url }
    API->>Security: Validate SSRF & Allowlist Domain
    Security-->>API: Domain Allowed
    API->>Registry: Fetch Live Offer
    Registry->>Scraper: Execute Proxy Scrape
    Scraper-->>Registry: Return Cleaned HTML / JSON
    Registry-->>API: Return Normalized Offer
    API->>DB: Log Fact to fact_price_history
    API->>ML: Run Price Forecast (History + Current Price)
    ML-->>API: Return Prediction (min_price_14d, drop_prob)
    API->>Gate: Evaluate 7 Hard Safety Gates
    Gate-->>API: Return Gate Result (Passed / Failed)
    API->>Synth: Synthesize Decision JSON
    Synth-->>API: Return DecisionSchema
    API-->>Frontend: HTTP 200 OK (Decision JSON)
    Frontend-->>User: Render Decision Card (BUY/WAIT/etc.)
```

---

### 8. Activity Diagram — Buy/Wait Decision Logic Flow

Step-by-step control logic evaluated by `DecisionSynthesizer`.

```mermaid
stateDiagram-v2
    [*] --> ReceiveProduct
    ReceiveProduct --> EvaluateSafetyGates
    
    state EvaluateSafetyGates {
        [*] --> Check7Gates
        Check7Gates --> AllPassed: All 7 Gates Pass
        Check7Gates --> GateFailed: Any Gate Fails
    }

    GateFailed --> BlockBUY: Set Blocked Decision (CAUTION / WAIT / NO_DECISION)
    BlockBUY --> RenderOutput

    AllPassed --> CheckAlternativeOffers
    CheckAlternativeOffers --> CheckAltFound: Cheaper Verified Retailer Exists
    CheckAltFound --> SetCHECK_ALT: Decision = CHECK_ALT
    SetCHECK_ALT --> RenderOutput

    CheckAlternativeOffers --> EvaluateMLForecast: No Cheaper Competitor

    state EvaluateMLForecast {
        [*] --> RunPriceTrendV2
        RunPriceTrendV2 --> DropHighProb: Drop Prob >= 60%
        RunPriceTrendV2 --> DropMedProb: Drop Prob >= 50%
        RunPriceTrendV2 --> PriceOptimal: Drop Prob < 50%
    }

    DropHighProb --> SetWAIT: Decision = WAIT
    DropMedProb --> SetDONT_RUSH: Decision = DONT_RUSH
    PriceOptimal --> CheckLowestPrice: At 90-Day Low?
    CheckLowestPrice --> SetBUY: Yes -> Decision = BUY
    CheckLowestPrice --> SetYOUR_CALL: No -> Decision = YOUR_CALL

    SetWAIT --> RenderOutput
    SetDONT_RUSH --> RenderOutput
    SetBUY --> RenderOutput
    SetYOUR_CALL --> RenderOutput

    RenderOutput --> [*]
```

---

### 9. Deployment Diagram

Physical deployment topology mapping client devices, API servers, proxy cloud, and database infrastructure.

```mermaid
graph TB
    subgraph Client Environments
        Browser[Desktop Browser\nChrome / Edge / Safari]
        ExtSidePanel[Chrome MV3 Extension\nNative Side Panel]
    end

    subgraph Production Cloud Server / Render / AWS
        FastAPIHost[Uvicorn ASGI Server\nFastAPI 0.109 / Python 3.11]
    end

    subgraph External Scraper Gateway
        ScraperAPICloud[ScraperAPI Infrastructure\nProxy Rotation & JS Engine]
    end

    subgraph Managed Cloud Database
        SupabaseHost[Supabase Cloud PostgreSQL 15\nOLTP Tables & DWDM Star Schema]
    end

    Browser -->|HTTPS / WSS| FastAPIHost
    ExtSidePanel -->|HTTPS / WSS| FastAPIHost
    FastAPIHost -->|HTTPS API Key| ScraperAPICloud
    FastAPIHost -->|TLS / PgBouncer| SupabaseHost
```

---

### 10. DWDM Star Schema Diagram

Dimensional model showing central Fact tables (`fact_price_history`, `fact_recommendation`) connected to Conformed Dimensions (`dim_product`, `dim_variant`, `dim_retailer`, `dim_seller`, `dim_category`, `dim_date`).

```mermaid
erDiagram
    FACT_PRICE_HISTORY }|--|| DIM_PRODUCT : references
    FACT_PRICE_HISTORY }|--|| DIM_VARIANT : references
    FACT_PRICE_HISTORY }|--|| DIM_RETAILER : references
    FACT_PRICE_HISTORY }|--|| DIM_SELLER : references
    FACT_PRICE_HISTORY }|--|| DIM_DATE : references

    FACT_RECOMMENDATION }|--|| DIM_PRODUCT : references
    FACT_RECOMMENDATION }|--|| DIM_DATE : references

    DIM_PRODUCT }|--|| DIM_CATEGORY : classified_by

    FACT_PRICE_HISTORY {
        bigint price_observation_id PK
        string variant_id FK
        string retailer_id FK
        string seller_id FK
        int date_key FK
        timestamp observed_at
        decimal price
        decimal shipping_cost
        boolean in_stock
    }

    FACT_RECOMMENDATION {
        string recommendation_id PK
        string product_id FK
        int date_key FK
        timestamp timestamp
        string decision
        decimal buy_point
        string confidence_level
        string primary_reason
    }

    DIM_PRODUCT {
        bigint product_key PK
        string product_id UNIQUE
        string brand
        string canonical_name
        string category_id FK
    }

    DIM_VARIANT {
        bigint variant_key PK
        string variant_id UNIQUE
        string model_number
        string storage
        string color
    }

    DIM_RETAILER {
        bigint retailer_key PK
        string retailer_id UNIQUE
        string retailer_name
        decimal reliability_score
    }

    DIM_SELLER {
        bigint seller_key PK
        string seller_id UNIQUE
        string seller_name
        decimal rating
        string reliability_tier
    }

    DIM_DATE {
        int date_key PK
        date full_date
        int month_number
        int quarter
        int year_number
        boolean is_weekend
    }
```
