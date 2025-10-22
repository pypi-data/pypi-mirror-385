"""
Core Projection Classes

These classes define data shaping operations (what data to return and
how to transform it) as opposed to specifications which define filtering
operations (what data to include/exclude).
"""

from .fields import *
from .grouping import *
from .limiting import *
from .ordering import *
from .query import *

__all__ = [
    # Field projections
    "FieldProjection",
    "AggregateProjection",
    "AggregateFunction",
    "ProjectionList",
    # Grouping
    "GroupingProjection",
    # Ordering
    "OrderingProjection",
    "OrderingList",
    # Limiting
    "LimitProjection",
    # Complete query projection
    "QueryProjection",
    "QueryProjectionBuilder",
    # Convenience functions
    "select",
    "select_distinct",
    "count",
]
