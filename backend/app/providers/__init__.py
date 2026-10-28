"""ShopQ Provider and Data Collection Subsystem.

Exports:
- ProviderRegistry and singleton provider_registry
- ScraperAPIProvider (primary live data provider)
- MockProvider (100% reliable fallback covering all 12 scenarios)
- Specific retailer adapters (Amazon, Flipkart, Croma, Reliance Digital, Myntra)
- Deterministic extraction pipeline (5-stage deterministic priority)
- Demand-driven ingestion triggers
"""

from app.providers.models import (
    ProviderStatus,
    ExtractionStage,
    ConfidenceLevel,
    ProviderOffer,
)
from app.providers.base import BaseProvider
from app.providers.registry import ProviderRegistry, provider_registry
from app.providers.scraperapi_provider import ScraperAPIProvider
from app.providers.firecrawl_provider import FirecrawlProvider
from app.providers.adapters import (
    MockProvider,
    AmazonProvider,
    FlipkartProvider,
    CromaProvider,
    RelianceDigitalProvider,
    MyntraProvider,
)
from app.providers.pipeline import (
    ExtractionPipeline,
    extraction_pipeline,
    JsonLdExtractor,
    SelectorExtractor,
    DomHeuristicsExtractor,
    RegexExtractor,
    LlmFallbackExtractor,
)
from app.providers.ingestion import (
    DemandDrivenTriggerHandler,
    trigger_handler,
)

__all__ = [
    "ProviderStatus",
    "ExtractionStage",
    "ConfidenceLevel",
    "ProviderOffer",
    "BaseProvider",
    "ProviderRegistry",
    "provider_registry",
    "ScraperAPIProvider",
    "FirecrawlProvider",
    "MockProvider",
    "AmazonProvider",
    "FlipkartProvider",
    "CromaProvider",
    "RelianceDigitalProvider",
    "MyntraProvider",
    "ExtractionPipeline",
    "extraction_pipeline",
    "JsonLdExtractor",
    "SelectorExtractor",
    "DomHeuristicsExtractor",
    "RegexExtractor",
    "LlmFallbackExtractor",
    "DemandDrivenTriggerHandler",
    "trigger_handler",
]
