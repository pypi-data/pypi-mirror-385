"""
Usage Examples for the Fractal Projections Library

This file demonstrates how to use the fractal_projections library
for building database-agnostic query projections.

ARCHITECTURE OVERVIEW:
- Projections: Database-agnostic data shaping definitions (NOT specifications!)
- Builders: Database-specific query generation
  - PostgresProjectionBuilder: Converts projections to PostgreSQL SQL
  - MongoProjectionBuilder: Converts projections to MongoDB aggregation pipelines
  - FirestoreProjectionBuilder: Converts projections to Firestore query configs
  - ElasticsearchProjectionBuilder: Converts projections to ES query DSL

This separation allows the same projections to work across
different databases with optimized native queries for each backend.
"""

from fractal_specifications.generic.collections import AndSpecification
from fractal_specifications.generic.operators import (
    EqualsSpecification,
    GreaterThanSpecification,
    InSpecification,
)

from .projections import (
    AggregateFunction,
    AggregateProjection,
    FieldProjection,
    GroupingProjection,
    LimitProjection,
    OrderingList,
    OrderingProjection,
    ProjectionList,
    QueryProjection,
    QueryProjectionBuilder,
    count,
    select_distinct,
)


def example_basic_select():
    """Basic field selection with filtering"""
    # SELECT organization_id, query FROM syncevent WHERE success = true
    query_projection = QueryProjection(
        filter=EqualsSpecification("success", True),
        projection=ProjectionList(
            [FieldProjection("organization_id"), FieldProjection("query")]
        ),
    )
    return query_projection


def example_distinct_select():
    """SELECT DISTINCT with ordering"""
    # SELECT DISTINCT organization_id FROM syncevent ORDER BY organization_id
    query_projection = QueryProjection(
        projection=ProjectionList([FieldProjection("organization_id")], distinct=True),
        ordering=OrderingList([OrderingProjection("organization_id")]),
    )
    return query_projection


def example_aggregates():
    """Aggregation queries without grouping"""
    # SELECT COUNT(*), AVG(rows), MAX(extraction_ts) FROM syncevent WHERE success = true
    query_projection = QueryProjection(
        filter=EqualsSpecification("success", True),
        projection=ProjectionList(
            [
                AggregateProjection(AggregateFunction.COUNT),
                AggregateProjection(AggregateFunction.AVG, "rows", "avg_rows"),
                AggregateProjection(
                    AggregateFunction.MAX, "extraction_ts", "latest_extraction"
                ),
            ]
        ),
    )
    return query_projection


def example_group_by():
    """Grouping with aggregates"""
    # SELECT organization_id, COUNT(*), SUM(rows)
    # FROM syncevent
    # WHERE success = true
    # GROUP BY organization_id
    # ORDER BY COUNT(*) DESC
    query_projection = QueryProjection(
        filter=EqualsSpecification("success", True),
        projection=ProjectionList(
            [
                FieldProjection("organization_id"),
                AggregateProjection(AggregateFunction.COUNT, alias="total_syncs"),
                AggregateProjection(AggregateFunction.SUM, "rows", "total_rows"),
            ]
        ),
        grouping=GroupingProjection(["organization_id"]),
        ordering=OrderingList([OrderingProjection("total_syncs", ascending=False)]),
    )
    return query_projection


def example_complex_query():
    """Complex query with multiple conditions, grouping, and limits"""
    complex_filter = AndSpecification(
        [
            EqualsSpecification("success", True),
            GreaterThanSpecification("rows", 100),
            InSpecification("organization_id", ["org1", "org2"]),
        ]
    )

    query_projection = QueryProjection(
        filter=complex_filter,
        projection=ProjectionList(
            [
                FieldProjection("organization_id"),
                FieldProjection("connection_id"),
                AggregateProjection(AggregateFunction.COUNT, alias="sync_count"),
                AggregateProjection(AggregateFunction.AVG, "rows", "avg_rows"),
            ]
        ),
        grouping=GroupingProjection(["organization_id", "connection_id"]),
        ordering=OrderingList(
            [
                OrderingProjection("avg_rows", ascending=False),
                OrderingProjection("sync_count", ascending=False),
            ]
        ),
        limiting=LimitProjection(10, 20),
    )
    return query_projection


def example_builder_pattern():
    """Using the fluent builder pattern"""

    # Simple distinct select
    query1 = select_distinct("organization_id").order_by("organization_id").build()

    # Count query
    query2 = count().filter(EqualsSpecification("success", True)).build()

    # Complex aggregation with grouping
    query3 = (
        QueryProjectionBuilder()
        .filter(EqualsSpecification("success", True))
        .select("organization_id", "connection_id")
        .count(alias="total_syncs")
        .avg("rows", "avg_rows")
        .sum("rows", "total_rows")
        .group_by("organization_id", "connection_id")
        .order_by_desc("total_syncs")
        .order_by("organization_id")
        .limit(50)
        .build()
    )

    return [query1, query2, query3]


def example_count_distinct():
    """COUNT DISTINCT queries"""
    # SELECT COUNT(DISTINCT organization_id) FROM syncevent WHERE success = true
    query_projection = QueryProjection(
        filter=EqualsSpecification("success", True),
        projection=ProjectionList(
            [
                AggregateProjection(
                    AggregateFunction.COUNT_DISTINCT, "organization_id", "unique_orgs"
                )
            ]
        ),
    )
    return query_projection


# Usage with different database backends:
"""
# PostgreSQL Repository
def get_stats_postgres(repository):
    from .builders import PostgresProjectionBuilder

    query_projection = example_group_by()

    if hasattr(repository, 'find_with_projection'):
        # Build SQL using PostgresProjectionBuilder
        builder = PostgresProjectionBuilder
        sql_parts = {
            'select': builder.build_select(query_projection.projection),
            'group_by': builder.build_group_by(query_projection.grouping),
            'order_by': builder.build_order_by(query_projection.ordering)
        }
        results = repository.find_with_projection(query_projection, sql_parts)
        return results
    else:
        # Fallback to in-memory processing
        all_events = list(repository.find(query_projection.filter))
        return list(query_projection.projection.apply_to_results(all_events))


# MongoDB Repository
def get_stats_mongo(repository):
    from .builders import MongoProjectionBuilder

    query_projection = example_group_by()

    if hasattr(repository, 'find_with_aggregation'):
        # Build aggregation pipeline using MongoProjectionBuilder
        pipeline = MongoProjectionBuilder.build_pipeline(
            query_projection.projection,
            query_projection.grouping,
            query_projection.ordering,
            query_projection.limiting
        )
        results = list(repository.find_with_aggregation(pipeline))
        return results
    else:
        # Fallback to in-memory processing
        all_events = list(repository.find(query_projection.filter))
        return list(query_projection.projection.apply_to_results(all_events))


# Firestore Repository
def get_stats_firestore(repository):
    from .builders import FirestoreProjectionBuilder

    query_projection = example_group_by()

    if hasattr(repository, 'find_with_projection'):
        # Check if query needs client-side processing
        builder = FirestoreProjectionBuilder
        if builder.requires_client_processing(query_projection.projection):
            # Complex aggregations need client-side processing
            all_events = list(repository.find(query_projection.filter))
            return list(query_projection.projection.apply_to_results(all_events))
        else:
            # Simple queries can use Firestore's native capabilities
            query_config = builder.build_query_config(
                query_projection.projection
            )
            results = list(
                repository.find_with_projection(query_projection, query_config)
            )
            return results
    else:
        # Fallback to in-memory processing
        all_events = list(repository.find(query_projection.filter))
        return list(query_projection.projection.apply_to_results(all_events))


# Elasticsearch Repository
def get_stats_elasticsearch(repository):
    from .builders import ElasticsearchProjectionBuilder

    query_projection = example_group_by()

    if hasattr(repository, 'find_with_query_dsl'):
        # Build Elasticsearch query DSL
        es_query = ElasticsearchProjectionBuilder.build_query(
            query_projection.projection,
            query_projection.grouping,
            query_projection.ordering,
            query_projection.limiting
        )
        results = list(repository.find_with_query_dsl(es_query))
        return results
    else:
        # Fallback to in-memory processing
        all_events = list(repository.find(query_projection.filter))
        return list(query_projection.projection.apply_to_results(all_events))
"""
