"""XcodeCloud build API operations."""

from collections.abc import Callable
from typing import Any

from app_store_connect_mcp.core.errors import ValidationError
from app_store_connect_mcp.core.protocols import APIClient
from app_store_connect_mcp.core.query_builder import APIQueryBuilder
from app_store_connect_mcp.domains.xcode_cloud.constants import (
    BUILD_FILTER_MAPPING,
    FIELDS_CI_ARTIFACTS,
    FIELDS_CI_BUILD_RUNS,
    FIELDS_CI_ISSUES,
    FIELDS_CI_TEST_RESULTS,
)
from app_store_connect_mcp.models import (
    CiBuildRunResponse,
    CiBuildRunsResponse,
)


async def list_builds(
    api: APIClient,
    product_id: str | None = None,
    workflow_id: str | None = None,
    filters: dict | None = None,
    sort: str = "-number",
    limit: int = 50,
    include: list[str] | None = None,
) -> dict[str, Any]:
    """List builds for a product or workflow."""
    # Determine the appropriate endpoint
    if workflow_id:
        endpoint = f"/v1/ciWorkflows/{workflow_id}/buildRuns"
    elif product_id:
        endpoint = f"/v1/ciProducts/{product_id}/buildRuns"
    else:
        raise ValidationError(
            "Missing required parameter: either product_id or workflow_id must be provided",
            details={"product_id": product_id, "workflow_id": workflow_id},
        )

    # Build query with common parameters
    query = (
        APIQueryBuilder(endpoint)
        .with_limit_and_sort(limit, sort)
        .with_filters(filters, BUILD_FILTER_MAPPING)
        .with_fields("ciBuildRuns", FIELDS_CI_BUILD_RUNS)
        .with_includes(include)
    )

    return await query.execute(api, CiBuildRunsResponse)


async def get_build(
    api: APIClient,
    build_id: str,
    include: list[str] | None = None,
) -> dict[str, Any]:
    """Get detailed information about a specific build."""
    endpoint = f"/v1/ciBuildRuns/{build_id}"

    query = (
        APIQueryBuilder(endpoint)
        .with_fields("ciBuildRuns", FIELDS_CI_BUILD_RUNS)
        .with_includes(include)
    )

    return await query.execute(api, CiBuildRunResponse)


async def _fetch_action_resources(
    api: APIClient,
    build_id: str,
    resource_endpoint_suffix: str,
    resource_fields_name: str,
    resource_fields: list[str],
    action_fields: list[str],
    limit: int,
    filter_actions: Callable[[dict], bool] | None = None,
) -> dict[str, Any]:
    """Helper to fetch resources from build actions:

    1. Fetching all actions for a build
    2. Iterating through actions to get their resources
    3. Augmenting resources with action context

    Args:
        api: API client
        build_id: Build run ID
        resource_endpoint_suffix: Endpoint suffix after /v1/ciBuildActions/{action_id}/
        resource_fields_name: Field name for the resource (e.g., "ciArtifacts")
        resource_fields: Fields to request for the resource
        action_fields: Fields to request for actions
        limit: Max resources per action
        filter_actions: Optional filter to only process certain actions
    """
    # 1 - get build actions for build run
    actions_endpoint = f"/v1/ciBuildRuns/{build_id}/actions"
    actions_query = (
        APIQueryBuilder(actions_endpoint)
        .with_limit_and_sort(200)
        .with_fields("ciBuildActions", action_fields)
    )

    actions_response = await actions_query.execute(api)

    # 2 - collect all resources from all actions
    all_resources = []
    actions_data = actions_response.get("data", [])

    for action in actions_data:
        action_id = action.get("id")

        if filter_actions and not filter_actions(action):
            continue

        if action_id:
            resource_endpoint = f"/v1/ciBuildActions/{action_id}/{resource_endpoint_suffix}"
            resource_query = (
                APIQueryBuilder(resource_endpoint)
                .with_limit_and_sort(limit)
                .with_fields(resource_fields_name, resource_fields)
            )

            resource_response = await resource_query.execute(api)
            resources = resource_response.get("data", [])

            for resource in resources:
                resource["_action"] = {
                    "id": action_id,
                    "name": action.get("attributes", {}).get("name"),
                    "actionType": action.get("attributes", {}).get("actionType"),
                }
                all_resources.append(resource)

    # 3 - return resources as response
    return {
        "data": all_resources,
        "meta": {"total": len(all_resources)},
    }


async def start_build(
    api: APIClient,
    workflow_id: str,
    source_branch_or_tag: str | None = None,
    pull_request_number: int | None = None,
) -> dict[str, Any]:
    """Start a new build for a workflow."""
    endpoint = "/v1/ciBuildRuns"

    # Prepare the request data
    request_data = {
        "data": {
            "type": "ciBuildRuns",
            "relationships": {"workflow": {"data": {"type": "ciWorkflows", "id": workflow_id}}},
        }
    }

    # Add source branch/tag or pull request if specified
    if source_branch_or_tag:
        request_data["data"]["relationships"]["sourceBranchOrTag"] = {
            "data": {"type": "scmGitReferences", "id": source_branch_or_tag}
        }

    if pull_request_number:
        request_data["data"]["relationships"]["pullRequest"] = {
            "data": {"type": "scmPullRequests", "id": str(pull_request_number)}
        }

    # Make the POST request
    response = await api.post(endpoint, data=request_data)

    # Parse with the model if available
    try:
        parsed = CiBuildRunResponse.model_validate(response)
        return parsed.model_dump(mode="json")
    except Exception:
        return response


async def list_artifacts(
    api: APIClient,
    build_id: str,
    limit: int = 50,
) -> dict[str, Any]:
    """List artifacts for a build."""
    return await _fetch_action_resources(
        api=api,
        build_id=build_id,
        resource_endpoint_suffix="artifacts",
        resource_fields_name="ciArtifacts",
        resource_fields=FIELDS_CI_ARTIFACTS,
        action_fields=["name", "actionType"],
        limit=limit,
    )


async def list_issues(
    api: APIClient,
    build_id: str,
    limit: int = 100,
) -> dict[str, Any]:
    """List issues for a build."""
    return await _fetch_action_resources(
        api=api,
        build_id=build_id,
        resource_endpoint_suffix="issues",
        resource_fields_name="ciIssues",
        resource_fields=FIELDS_CI_ISSUES,
        action_fields=["name", "actionType", "issueCounts"],
        limit=limit,
    )


async def list_test_results(
    api: APIClient,
    build_id: str,
    limit: int = 100,
) -> dict[str, Any]:
    """List test results for a build."""

    # Filter to only process TEST actions
    def is_test_action(action: dict) -> bool:
        action_type = action.get("attributes", {}).get("actionType")
        return action_type and "TEST" in str(action_type).upper()

    return await _fetch_action_resources(
        api=api,
        build_id=build_id,
        resource_endpoint_suffix="testResults",
        resource_fields_name="ciTestResults",
        resource_fields=FIELDS_CI_TEST_RESULTS,
        action_fields=["name", "actionType"],
        limit=limit,
        filter_actions=is_test_action,
    )
