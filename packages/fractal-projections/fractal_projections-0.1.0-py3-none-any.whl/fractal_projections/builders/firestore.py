"""
Firestore Projection Builder

Converts generic projections to Firestore query configuration.

Firestore has limited aggregation capabilities compared to SQL databases.
Most complex operations require client-side processing.
"""

from typing import Dict, List

from ..projections.fields import (
    AggregateFunction,
    AggregateProjection,
    FieldProjection,
    ProjectionList,
)
from ..projections.grouping import GroupingProjection
from ..projections.limiting import LimitProjection
from ..projections.ordering import OrderingList


class FirestoreProjectionBuilder:
    """Builds Firestore query configuration from projection objects"""

    @staticmethod
    def build_query_config(projection: ProjectionList) -> Dict:
        """
        Convert ProjectionList to Firestore query configuration

        Returns a config dict that tells the repository how to handle the query:
        - What can be done server-side (natively in Firestore)
        - What needs client-side processing
        """
        query_config = {}

        if not projection or not projection.fields:
            return query_config

        field_names = []
        has_aggregates = False

        for field_spec in projection.fields:
            if isinstance(field_spec, FieldProjection):
                field_names.append(field_spec.field)
            elif isinstance(field_spec, AggregateProjection):
                has_aggregates = True
                if field_spec.function == AggregateFunction.COUNT:
                    # Firestore supports COUNT queries natively
                    query_config["count_only"] = True
                    if field_spec.field:
                        # COUNT(field) - we'll need to filter non-null values
                        query_config["count_field"] = field_spec.field
                else:
                    # Other aggregates need client-side processing
                    query_config["client_side_aggregation"] = True
                    if field_spec.field:
                        field_names.append(field_spec.field)

        if field_names and not has_aggregates:
            # For simple field selection, we'll select all fields and filter client-side
            # Firestore doesn't have field-level projection in queries
            query_config["select_fields"] = field_names

        # DISTINCT handling (Firestore doesn't support DISTINCT natively)
        if projection.distinct:
            query_config["distinct"] = True
            query_config["client_side_processing"] = True

        return query_config

    @staticmethod
    def build_order_constraints(ordering: OrderingList) -> List[Dict]:
        """Convert OrderingList to Firestore order_by constraints"""
        if not ordering:
            return []

        order_constraints = []
        for order_proj in ordering:
            direction = "ASCENDING" if order_proj.ascending else "DESCENDING"
            order_constraints.append(
                {"field": order_proj.field, "direction": direction}
            )

        return order_constraints

    @staticmethod
    def build_limit_constraint(limit: LimitProjection) -> Dict:
        """Convert LimitProjection to Firestore limit constraint"""
        constraint = {"limit": limit.limit}

        # Firestore uses offset for pagination
        if limit.offset > 0:
            constraint["offset"] = limit.offset

        return constraint

    @staticmethod
    def requires_client_processing(projection: ProjectionList) -> bool:
        """
        Check if the projection requires client-side processing

        Firestore has limited server-side capabilities, so many operations
        need to be done client-side after retrieving documents.
        """
        if not projection:
            return False

        if projection.distinct:
            return True

        if projection.fields:
            for field_spec in projection.fields:
                if isinstance(field_spec, AggregateProjection):
                    # Only COUNT is supported server-side, others need client processing
                    if field_spec.function != AggregateFunction.COUNT:
                        return True
                    # COUNT DISTINCT needs client processing
                    if field_spec.function == AggregateFunction.COUNT_DISTINCT:
                        return True

        return False

    @staticmethod
    def build_native_count_query() -> Dict:
        """
        Build configuration for Firestore's native count query

        Firestore recently added count() aggregation queries which are
        more efficient than fetching all documents.
        """
        return {"use_count_aggregation": True, "server_side_only": True}

    @staticmethod
    def can_use_native_operations(
        projection: ProjectionList, grouping: GroupingProjection = None
    ) -> bool:
        """
        Check if the projection can use Firestore's native operations

        Returns True if the entire query can be handled server-side.
        """
        # Grouping is not supported natively
        if grouping:
            return False

        # Complex projections need client-side processing
        if FirestoreProjectionBuilder.requires_client_processing(projection):
            return False

        # Simple field selection or count-only can be native
        return True
