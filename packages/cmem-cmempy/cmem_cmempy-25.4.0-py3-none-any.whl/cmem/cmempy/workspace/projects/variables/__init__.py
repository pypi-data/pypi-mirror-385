"""API for working with project variables."""
import json
from typing import Union

from requests import HTTPError

from cmem.cmempy import config

from cmem.cmempy.api import send_request
from cmem.cmempy.workspace.projects.project import get_projects


def get_variables_uri():
    """Get endpoint URI pattern for variables list."""
    path = "/api/core/variableTemplate/variables?project={}"
    return config.get_di_api_endpoint() + path


def get_variable_uri():
    """Get endpoint URI pattern for a single variable"""
    path = "/api/core/variableTemplate/variables/{}?project={}"
    return config.get_di_api_endpoint() + path


def get_variables(project_name: str) -> list[dict]:
    """GET retrieve list of variables."""
    response = send_request(get_variables_uri().format(project_name), method="GET")
    parsed = json.loads(response.decode("utf-8"))["variables"]
    returned = []
    for _ in parsed:
        returned.append(dict(_))
    return returned


def get_variable(variable_name: str, project_name: str) -> Union[dict, bool]:
    """GET retrieve a single variable.

    or False if variable was not found.
    """
    try:
        response = send_request(
            get_variable_uri().format(variable_name, project_name), method="GET"
        )
    except HTTPError as error:
        if error.response is not None and error.response.status_code == 404:
            return False
        raise error
    return dict(json.loads(response.decode("utf-8")))


def delete_variable(variable_name: str, project_name: str):
    """DELETE a single variable."""
    send_request(
        get_variable_uri().format(variable_name, project_name), method="DELETE"
    )


def create_or_update_variable(variable_name: str, project_name: str, data: dict):
    """PUT create or update a single variable."""
    headers = {"Content-Type": "application/json"}
    send_request(
        get_variable_uri().format(variable_name, project_name),
        method="PUT",
        data=json.dumps(data),
        headers=headers,
    )


def get_all_variables() -> list[dict]:
    """Get all variables of all projects."""
    variables = []
    for project_id in [_["name"] for _ in get_projects()]:
        for variable in list(get_variables(project_id)):
            variable["project"] = project_id
            variable["id"] = project_id + ":" + variable["name"]
            variables.append(variable)
    return variables
