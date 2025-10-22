"""
Elasticsearch Projection Builder

Converts generic projections to Elasticsearch query DSL with aggregations.
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


class ElasticsearchProjectionBuilder:
    """Builds Elasticsearch query DSL from projection objects"""

    @staticmethod
    def build_query(
        projection: ProjectionList,
        grouping: GroupingProjection = None,
        ordering: OrderingList = None,
        limiting: LimitProjection = None,
    ) -> Dict:
        """
        Convert projections to Elasticsearch query DSL

        Returns an Elasticsearch query dict with aggregations like:
        {
            "size": 0,  # Don't return documents, just aggregations
            "aggs": {
                "organization_stats": {
                    "terms": {"field": "organization_id"},
                    "aggs": {
                        "total_rows": {"sum": {"field": "rows"}},
                        "avg_rows": {"avg": {"field": "rows"}}
                    }
                }
            }
        }
        """
        query = {}

        if not projection or not projection.fields:
            # Simple query without aggregations
            if limiting:
                query["size"] = limiting.limit
                if limiting.offset > 0:
                    query["from"] = limiting.offset
            return query

        # Handle aggregations
        if projection.has_aggregates() or grouping:
            # Use aggregations - don't return documents
            query["size"] = 0
            query["aggs"] = ElasticsearchProjectionBuilder._build_aggregations(
                projection, grouping
            )
        else:
            # Simple field selection
            source_fields = [
                field.field
                for field in projection.fields
                if isinstance(field, FieldProjection)
            ]
            if source_fields:
                query["_source"] = source_fields

            # Add pagination
            if limiting:
                query["size"] = limiting.limit
                if limiting.offset > 0:
                    query["from"] = limiting.offset

        # Add sorting (only for non-aggregation queries)
        if ordering and not (projection.has_aggregates() or grouping):
            query["sort"] = ElasticsearchProjectionBuilder._build_sort(ordering)

        return query

    @staticmethod
    def _build_aggregations(
        projection: ProjectionList, grouping: GroupingProjection = None
    ) -> Dict:
        """Build Elasticsearch aggregations"""
        aggs = {}

        if grouping:
            # Terms aggregation for grouping
            group_field = grouping.fields[0]  # ES typically groups by one field
            agg_name = f"grouped_by_{group_field}"

            aggs[agg_name] = {
                "terms": {
                    "field": group_field,
                    "size": 10000,  # Large enough to get all groups
                }
            }

            # Sub-aggregations for metrics
            sub_aggs = {}
            for field_spec in projection.fields:
                if isinstance(field_spec, AggregateProjection):
                    sub_agg = ElasticsearchProjectionBuilder._build_metric_aggregation(
                        field_spec
                    )
                    if sub_agg:
                        agg_key = (
                            field_spec.alias
                            or f"{field_spec.function.value.lower()}_{field_spec.field}"
                        )
                        sub_aggs[agg_key] = sub_agg

            if sub_aggs:
                aggs[agg_name]["aggs"] = sub_aggs

        else:
            # Global aggregations (no grouping)
            for field_spec in projection.fields:
                if isinstance(field_spec, AggregateProjection):
                    agg = ElasticsearchProjectionBuilder._build_metric_aggregation(
                        field_spec
                    )
                    if agg:
                        func_name = field_spec.function.value.lower()
                        field_name = field_spec.field or "all"
                        agg_key = field_spec.alias or f"{func_name}_{field_name}"
                        aggs[agg_key] = agg

        return aggs

    @staticmethod
    def _build_metric_aggregation(agg_proj: AggregateProjection) -> Dict:
        """Build individual metric aggregation"""
        if agg_proj.function == AggregateFunction.COUNT:
            return (
                {"value_count": {"field": agg_proj.field}}
                if agg_proj.field
                else {"value_count": {"field": "_id"}}
            )

        elif agg_proj.function == AggregateFunction.COUNT_DISTINCT:
            return {"cardinality": {"field": agg_proj.field}}

        elif agg_proj.function == AggregateFunction.SUM:
            return {"sum": {"field": agg_proj.field}}

        elif agg_proj.function == AggregateFunction.AVG:
            return {"avg": {"field": agg_proj.field}}

        elif agg_proj.function == AggregateFunction.MIN:
            return {"min": {"field": agg_proj.field}}

        elif agg_proj.function == AggregateFunction.MAX:
            return {"max": {"field": agg_proj.field}}

        return {}

    @staticmethod
    def _build_sort(ordering: OrderingList) -> List[Dict]:
        """Build Elasticsearch sort configuration"""
        sort_configs = []

        for order_proj in ordering:
            sort_config = {
                order_proj.field: {"order": "asc" if order_proj.ascending else "desc"}
            }
            sort_configs.append(sort_config)

        return sort_configs

    @staticmethod
    def build_search_after_query(
        projection: ProjectionList,
        search_after_values: List,
        ordering: OrderingList = None,
        limiting: LimitProjection = None,
    ) -> Dict:
        """
        Build query with search_after for efficient pagination

        This is more efficient than offset-based pagination for large datasets.
        """
        query = ElasticsearchProjectionBuilder.build_query(
            projection, None, ordering, limiting
        )

        if search_after_values:
            query["search_after"] = search_after_values

        return query
