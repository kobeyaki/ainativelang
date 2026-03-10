"""
Adapters: pluggable backends for R (db, api), P (pay), Sc (scrape).
Replace mock adapters with real implementations (Prisma, Stripe, etc.).
"""
from .base import (
    AdapterRegistry,
    APIAdapter,
    AuthAdapter,
    CacheAdapter,
    DBAdapter,
    PayAdapter,
    QueueAdapter,
    ScrapeAdapter,
    TxnAdapter,
)
from .mock import mock_registry

__all__ = [
    "AdapterRegistry",
    "DBAdapter",
    "APIAdapter",
    "AuthAdapter",
    "CacheAdapter",
    "PayAdapter",
    "QueueAdapter",
    "ScrapeAdapter",
    "TxnAdapter",
    "mock_registry",
]
