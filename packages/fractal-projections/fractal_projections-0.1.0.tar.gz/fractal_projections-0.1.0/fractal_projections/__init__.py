"""
Fractal Projections Library

A comprehensive projection system for defining how data should be shaped,
aggregated, grouped, ordered, and limited in database queries.

This library complements fractal_specifications (which handles filtering)
by providing data shaping capabilities.
"""

from .builders import *
from .projections import *

__version__ = "0.1.0"

__all__ = [
    # Core projections
    "FieldProjection",
    "AggregateProjection",
    "AggregateFunction",
    "ProjectionList",
    "GroupingProjection",
    "OrderingProjection",
    "OrderingList",
    "LimitProjection",
    "QueryProjection",
    # Builder pattern
    "QueryProjectionBuilder",
    # Convenience functions
    "select",
    "select_distinct",
    "count",
    # Builders (for when you need database-specific functionality)
    "PostgresProjectionBuilder",
    "MongoProjectionBuilder",
    "FirestoreProjectionBuilder",
    "ElasticsearchProjectionBuilder",
]
