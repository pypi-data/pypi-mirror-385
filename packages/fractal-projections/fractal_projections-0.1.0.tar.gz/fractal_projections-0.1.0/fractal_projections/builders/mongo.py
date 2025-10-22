"""
MongoDB Projection Builder

Converts generic projections to MongoDB aggregation pipeline stages.
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


class MongoProjectionBuilder:
    """Builds MongoDB aggregation pipeline from projection objects"""

    @staticmethod
    def build_pipeline(
        projection: ProjectionList,
        grouping: GroupingProjection = None,
        ordering: OrderingList = None,
        limiting: LimitProjection = None,
    ) -> List[Dict]:
        """
        Build complete MongoDB aggregation pipeline

        Returns a list of pipeline stages like:
        [
            {"$group": {...}},
            {"$sort": {...}},
            {"$limit": 10}
        ]
        """
        pipeline = []

        # Handle projection and grouping together
        if projection and projection.fields:
            if grouping or projection.has_aggregates():
                # Build $group stage
                group_stage = MongoProjectionBuilder._build_group_stage(
                    projection, grouping
                )
                if group_stage:
                    pipeline.append(group_stage)
            else:
                # Simple field projection - use $project
                project_stage = MongoProjectionBuilder._build_project_stage(projection)
                if project_stage:
                    pipeline.append(project_stage)

        # Add sorting
        if ordering:
            sort_stage = MongoProjectionBuilder._build_sort_stage(ordering)
            if sort_stage:
                pipeline.append(sort_stage)

        # Add limiting
        if limiting:
            if limiting.offset > 0:
                pipeline.append({"$skip": limiting.offset})
            pipeline.append({"$limit": limiting.limit})

        return pipeline

    @staticmethod
    def _build_project_stage(projection: ProjectionList) -> Dict:
        """Build MongoDB $project stage for simple field selection"""
        project_fields = {}

        for field_spec in projection.fields:
            if isinstance(field_spec, FieldProjection):
                key = field_spec.alias or field_spec.field
                project_fields[key] = f"${field_spec.field}"

        if not project_fields:
            return {}

        return {"$project": project_fields}

    @staticmethod
    def _build_group_stage(
        projection: ProjectionList, grouping: GroupingProjection = None
    ) -> Dict:
        """Build MongoDB $group stage for aggregations"""
        group_spec = {}

        # Group by fields
        if grouping:
            if len(grouping.fields) == 1:
                group_spec["_id"] = f"${grouping.fields[0]}"
            else:
                group_spec["_id"] = {field: f"${field}" for field in grouping.fields}
        else:
            # No grouping - aggregate all documents
            group_spec["_id"] = None

        # Add aggregations
        for field_spec in projection.fields:
            if isinstance(field_spec, AggregateProjection):
                func_name = field_spec.function.value.lower()
                field_name = field_spec.field or "all"
                key = field_spec.alias or f"{func_name}_{field_name}"

                if field_spec.function == AggregateFunction.COUNT:
                    group_spec[key] = {"$sum": 1}
                elif field_spec.function == AggregateFunction.COUNT_DISTINCT:
                    group_spec[key] = {"$addToSet": f"${field_spec.field}"}
                elif field_spec.function == AggregateFunction.SUM:
                    group_spec[key] = {"$sum": f"${field_spec.field}"}
                elif field_spec.function == AggregateFunction.AVG:
                    group_spec[key] = {"$avg": f"${field_spec.field}"}
                elif field_spec.function == AggregateFunction.MIN:
                    group_spec[key] = {"$min": f"${field_spec.field}"}
                elif field_spec.function == AggregateFunction.MAX:
                    group_spec[key] = {"$max": f"${field_spec.field}"}

            elif isinstance(field_spec, FieldProjection):
                # Include grouped fields in output
                if grouping and field_spec.field in grouping.fields:
                    key = field_spec.alias or field_spec.field
                    if len(grouping.fields) == 1:
                        group_spec[key] = "$_id"
                    else:
                        group_spec[key] = f"$_id.{field_spec.field}"

        return {"$group": group_spec} if len(group_spec) > 1 else {}

    @staticmethod
    def _build_sort_stage(ordering: OrderingList) -> Dict:
        """Build MongoDB $sort stage"""
        sort_spec = {}

        for order_proj in ordering:
            sort_spec[order_proj.field] = 1 if order_proj.ascending else -1

        return {"$sort": sort_spec} if sort_spec else {}

    @staticmethod
    def build_count_distinct_pipeline(field: str) -> List[Dict]:
        """
        Build pipeline for COUNT DISTINCT operations

        MongoDB's $addToSet returns an array, so we need additional stages
        to count the array length.
        """
        return [
            {"$group": {"_id": None, "distinct_values": {"$addToSet": f"${field}"}}},
            {"$project": {"_id": 0, "count": {"$size": "$distinct_values"}}},
        ]
