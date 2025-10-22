"""API for managing conditions in DP."""
import json
from typing import Optional, Union

from cmem.cmempy import config

from cmem.cmempy.api import request


def get_authorization_uri():
    """Get graph URI of the authorization conditions graph."""
    path = "/api/authorization"
    return config.get_dp_api_endpoint() + path


def get_acls(page: int = 0):
    """GET access conditions."""
    return request(get_authorization_uri(), method="GET", params={"page": page})


def fetch_all_acls() -> list:
    """Fetch all the access conditions"""
    acls: list[dict] = []
    page: int = 0
    while True:
        result = get_acls(page=page).json()
        acls += result["content"]
        # CMEM-6362: until 24.3, we had a serialization, where 'last' was explicit
        # last = True -> last page (old page model)
        # last = False -> not last page (old page model)
        # KeyError -> new page model, lets check number and totalPages
        last_indicator = False
        try:
            last_indicator = result["last"]
        except KeyError:
            number = int(result["page"]["number"]) + 1  # starts with 0
            total = int(result["page"]["totalPages"])
            if number >= total:
                last_indicator = True
        if last_indicator is True:
            break
        page += 1
    return acls


# pylint: disable-msg=too-many-arguments
def update_access_condition(
    iri,
    name=None,
    description=None,
    user=None,
    groups=None,
    read_graphs=None,
    write_graphs=None,
    actions=None,
    read_graph_patterns=None,
    write_graph_patterns=None,
    action_patterns=None,
    query=None,
):
    """PUT access conditions."""
    payload = get_access_condition_by_iri(iri=iri).json()
    if name:
        payload["name"] = name
    if description:
        payload["comment"] = description
    if user:
        payload["requiresAccount"] = user
    if groups:
        payload["requiresGroup"] = groups
    if read_graphs:
        payload["readableGraphs"] = read_graphs
    if write_graphs:
        payload["writableGraphs"] = write_graphs
    if actions:
        payload["allowedActions"] = actions
    if read_graph_patterns:
        payload["grantReadPatterns"] = read_graph_patterns
    if write_graph_patterns:
        payload["grantWritePatterns"] = write_graph_patterns
    if action_patterns:
        payload["grantAllowedActions"] = action_patterns
    if query:
        payload["dynamicAccessConditionQuery"] = query

    payload = json.dumps(payload)
    content_type = "application/json"
    headers = {"accept": content_type, "Content-Type": content_type}
    return request(get_authorization_uri(), method="PUT", data=payload, headers=headers)


# pylint: disable-msg=too-many-arguments, too-many-locals
def create_access_condition(
    name: str,
    static_id: Optional[str] = None,
    description: Optional[str] = None,
    user: Optional[str] = None,
    groups: Optional[list[str]] = None,
    read_graphs: Optional[list[str]] = None,
    write_graphs: Optional[list[str]] = None,
    actions: Optional[list[str]] = None,
    read_graph_patterns: Optional[list[str]] = None,
    write_graph_patterns: Optional[list[str]] = None,
    action_patterns: Optional[list[str]] = None,
    query: Optional[str] = None,
):
    """POST access conditions."""
    payload = {
        "staticId": static_id,
        "name": name,
        "comment": description,
        "requiresAccount": user,
        "requiresGroup": groups,
        "readableGraphs": read_graphs,
        "writableGraphs": write_graphs,
        "allowedActions": actions,
        "grantReadPatterns": read_graph_patterns,
        "grantWritePatterns": write_graph_patterns,
        "grantAllowedActions": action_patterns,
        "dynamicAccessConditionQuery": query,
    }
    content_type = "application/json"
    data = json.dumps(payload).encode("utf-8")
    headers = {"accept": content_type, "Content-Type": content_type}
    return request(get_authorization_uri(), method="POST", headers=headers, data=data)


def delete_access_condition(iri):
    """DELETE access condition."""
    params = {"resource": iri}
    return request(get_authorization_uri(), method="DELETE", params=params)


def get_users():
    """GET users."""
    uri = get_authorization_uri() + "/users"
    return request(uri, method="GET")


def review_graph_rights(
        account_iri: Union[str, None] = None,
        group_iris: Union[list[str], None] = None
):
    """Review access rights for a given account and group."""
    uri = get_authorization_uri() + "/review"

    # query parameters
    params: dict[str, Union[str, list[str], None]] = {
        "accountIri": account_iri,
        "groupIris": group_iris
    }
    return request(uri, method="GET", params=params)


def get_access_condition_by_iri(iri: str):
    """Get access condition by iri."""
    uri = get_authorization_uri() + "/iri"
    params = {"resource": iri}
    return request(uri, method="GET", params=params)


def get_groups():
    """GET groups."""
    uri = get_authorization_uri() + "/groups"
    return request(uri, method="GET")


def get_actions():
    """GET actions."""
    uri = get_authorization_uri() + "/actions"
    return request(uri, method="GET")
