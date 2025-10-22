"""SHACL validation functions."""
from typing import Union

from cmem.cmempy import config
from cmem.cmempy.api import get_json, request

STATUS_SCHEDULED = "SCHEDULED"
STATUS_RUNNING = "RUNNING"
STATUS_FINISHED = "FINISHED"
STATUS_CANCELLED = "CANCELLED"
STATUS_ERROR = "ERROR"


def get_validation_api_endpoint() -> str:
    """Get endpoint URI for a SHACL Validation endpoint"""
    return str(config.get_dp_api_endpoint() + "/api/shacl/validation/batches")


def get_all_aggregations() -> list[dict]:
    """Get all batch validations (aggregation views)"""
    endpoint = get_validation_api_endpoint() + "/view/aggregation"
    return list(get_json(endpoint))


# pylint: disable-msg=too-many-arguments
def start(
    context_graph: str,
    shape_graph: Union[str, None] = None,
    query: Union[str, None] = None,
    result_graph: Union[str, None] = None,
    replace: bool = False,
    ignore_graph: Union[list[str], None] = None,
) -> str:
    """Start a single batch validation and return batch ID"""
    params: dict[str, Union[str, bool, list[str]]] = {"contextGraph": context_graph}
    if shape_graph:
        params["shapeGraph"] = shape_graph
    if query:
        params["selectionQuery"] = query
    if result_graph:
        params["validationResultsTargetGraph"] = result_graph
        params["replace"] = replace
    if ignore_graph:
        params["owlImportsIgnoreList"] = ignore_graph

    response = request(get_validation_api_endpoint(), params=params, method="POST")
    return str(response.headers.get("Location")).rsplit("/", maxsplit=1)[-1]


def get_aggregation(batch_id: str) -> dict:
    """Get a single batch validation (aggregation view)"""
    endpoint = get_validation_api_endpoint() + "/" + batch_id + "/view/aggregation"
    return dict(get_json(uri=endpoint))


def get(batch_id: str) -> dict:
    """Get a single batch validation"""
    endpoint = get_validation_api_endpoint() + "/" + batch_id
    return dict(get_json(uri=endpoint))


def cancel(batch_id: str) -> None:
    """Cancel a single batch validation"""
    endpoint = get_validation_api_endpoint() + "/" + batch_id
    request(uri=endpoint, method="DELETE")
