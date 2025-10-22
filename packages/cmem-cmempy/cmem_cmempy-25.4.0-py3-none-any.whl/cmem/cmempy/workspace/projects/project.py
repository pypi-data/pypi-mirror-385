"""API methods for working with one project."""
import json

from cmem.cmempy import config

from cmem.cmempy.api import send_request


def get_projects_uri():
    """Get endpoint URI for project list."""
    path = "/workspace/projects"
    return config.get_di_api_endpoint() + path


def get_project_uri():
    """Get endpoint URI pattern for a project."""
    path = "/workspace/projects/{}"
    return config.get_di_api_endpoint() + path


def get_projects_api_uri():
    """Get endpoint URI for the new projects API."""
    path = "/api/workspace/projects"
    return config.get_di_api_endpoint() + path


def get_project_api_uri():
    """Get endpoint URI pattern for a single project (new API)."""
    return get_projects_api_uri() + "/{}"


def get_generate_matching_link_rule_uri():
    """Get endpoint URI for generating an ontology matching linking rule"""
    path = "/ontologyMatching/generateMatchingLinkRule"
    return config.get_di_api_endpoint() + path


def get_projects():
    """GET all projects."""
    response = send_request(get_projects_uri(), method="GET")
    return json.loads(response.decode("utf-8"))


def get_project(name):
    """GET one project."""
    response = send_request(get_project_uri().format(name), method="GET")
    return json.loads(response.decode("utf-8"))


def reload_project(name):
    """Reload one project."""
    return send_request(get_project_uri().format(name) + "/reload", method="POST")


def get_prefixes(name):
    """GET prefixes of a project."""
    response = send_request(
        get_project_api_uri().format(name) + "/prefixes",
        method="GET",
        headers={"Accept": "application/json"},
    )
    return json.loads(response.decode("utf-8"))


def make_new_project(name):
    """PUT make new project."""
    response = send_request(get_project_uri().format(name), method="PUT")
    return json.loads(response.decode("utf-8"))


def make_new_project_with_metadata(id_: str, label: str = "", description: str = ""):
    """POST make new project including metadata"""
    # {"metaData":{"label":"test","description":"eee"},"id":"myid"}
    if label == "":
        label = id_
    data = {"id": id_, "metaData": {"label": label, "description": description}}
    response = send_request(
        get_projects_api_uri(),
        method="POST",
        headers={"Content-Type": "application/json"},
        data=json.dumps(data),
    )
    return json.loads(response.decode("utf-8"))


def delete_project(name):
    """DELETE remove project."""
    send_request(get_project_uri().format(name), method="DELETE")


def get_failed_tasks_report(name):
    """Get a report of tasks that could not be loaded in a project."""
    response = send_request(
        get_project_api_uri().format(name) + "/failedTasksReport",
        method="GET",
        headers={"Accept": "application/json"},
    )
    return json.loads(response.decode("utf-8"))


def create_project_with_transformation(
    transform_project_id,
    transform_task_id,
    matching_link_spec_project_id,
    matching_link_spec_id,
):
    """Generates an ontology matching linking rule in the
    specified project with the specified linking task ID"""
    data = {
        "transformProjectId": transform_project_id,
        "transformTaskId": transform_task_id,
        "matchingLinkSpecProjectId": matching_link_spec_project_id,
        "matchingLinkSpecId": matching_link_spec_id,
    }
    data = json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    params = None
    response = send_request(
        get_generate_matching_link_rule_uri(),
        data=data,
        headers=headers,
        method="POST",
        params=params,
    )
    return response
