"""XcodeCloud API methods for Xcode Cloud products and workflows."""

from typing import Any

from app_store_connect_mcp.core.protocols import APIClient
from app_store_connect_mcp.core.query_builder import APIQueryBuilder
from app_store_connect_mcp.domains.xcode_cloud.constants import (
    FIELDS_CI_PRODUCTS,
    FIELDS_CI_WORKFLOWS,
    PRODUCT_FILTER_MAPPING,
    WORKFLOW_FILTER_MAPPING,
)
from app_store_connect_mcp.models import (
    CiProductResponse,
    CiProductsResponse,
    CiWorkflowResponse,
    CiWorkflowsResponse,
)


async def list_products(
    api: APIClient,
    filters: dict | None = None,
    limit: int = 50,
    include: list[str] | None = None,
) -> dict[str, Any]:
    """List all Xcode Cloud products."""
    endpoint = "/v1/ciProducts"

    query = (
        APIQueryBuilder(endpoint)
        .with_limit_and_sort(limit)  # No sort parameter supported by API
        .with_filters(filters, PRODUCT_FILTER_MAPPING)
        .with_fields("ciProducts", FIELDS_CI_PRODUCTS)
        .with_includes(include)
    )

    return await query.execute(api, CiProductsResponse)


async def get_product(
    api: APIClient,
    product_id: str,
    include: list[str] | None = None,
) -> dict[str, Any]:
    """Get detailed information about a specific Xcode Cloud product."""
    endpoint = f"/v1/ciProducts/{product_id}"

    query = (
        APIQueryBuilder(endpoint)
        .with_fields("ciProducts", FIELDS_CI_PRODUCTS)
        .with_includes(include)
    )

    return await query.execute(api, CiProductResponse)


async def list_workflows(
    api: APIClient,
    product_id: str,
    filters: dict | None = None,
    limit: int = 50,
    include: list[str] | None = None,
) -> dict[str, Any]:
    """List workflows for a product.

    Note: This is a read-only operation. Create, update, and delete operations
    for workflows are not supported through this API for safety reasons.
    Workflow modifications should be done through Xcode or the App Store Connect web interface.
    """
    endpoint = f"/v1/ciProducts/{product_id}/workflows"

    query = (
        APIQueryBuilder(endpoint)
        .with_limit_and_sort(limit)  # No sort parameter supported by API
        .with_filters(filters, WORKFLOW_FILTER_MAPPING)
        .with_fields("ciWorkflows", FIELDS_CI_WORKFLOWS)
        .with_includes(include)
    )

    return await query.execute(api, CiWorkflowsResponse)


async def get_workflow(
    api: APIClient,
    workflow_id: str,
    include: list[str] | None = None,
) -> dict[str, Any]:
    """Get detailed information about a specific workflow.

    Note: This is a read-only operation. Create, update, and delete operations
    for workflows are not supported through this API for safety reasons.
    Workflow modifications should be done through Xcode or the App Store Connect web interface.
    """
    endpoint = f"/v1/ciWorkflows/{workflow_id}"

    query = (
        APIQueryBuilder(endpoint)
        .with_fields("ciWorkflows", FIELDS_CI_WORKFLOWS)
        .with_includes(include)
    )

    return await query.execute(api, CiWorkflowResponse)
