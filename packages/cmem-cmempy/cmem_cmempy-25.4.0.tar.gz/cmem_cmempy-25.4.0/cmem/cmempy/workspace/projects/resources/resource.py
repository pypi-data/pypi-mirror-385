"""API methods for working with single resources."""
import json
from typing import Optional
from urllib.parse import quote_plus

import requests
from cmem.cmempy import config

from cmem.cmempy.api import request, send_request


def get_resource_uri(
    project_name: Optional[str] = None,
    resource_name: Optional[str] = None,
    sub_path: Optional[str] = None,
) -> str:
    """
    Get the endpoint URI pattern for a resource OR get
    the full URI in case project and resource is given.

    Args:
        project_name: the project ID as a string
        resource_name: the resource path
        sub_path: None, "metadata" or "usage"

    Note: resource_name will be URL encoded before request.
    """
    path = "/workspace/projects/{}/files?path={}"
    # sub_path can be used to request a sub-API of the files API
    if sub_path:
        path = path.replace("files?", f"files/{sub_path}?")
    path = config.get_di_api_endpoint() + path
    if not project_name and not resource_name:
        return str(path)
    if project_name and resource_name:
        return str(path.format(project_name, quote_plus(resource_name)))
    raise ValueError(
        "Either give project_name AND resource_name or give none of them"
        " and get the pattern only."
    )


def get_resource(project_name, resource_name):
    """GET resource.

    Args:
        project_name (str): The project ID in the workspace.
        resource_name (str): The resource ID/name in the workspace.

    Returns:
        requests.Response object
    """
    resource_url = get_resource_uri(
        project_name=project_name, resource_name=resource_name
    )
    response = send_request(resource_url, method="GET")
    return response


def resource_exist(project_name, resource_name):
    """Check if a resource exist.

    A return value of true means the resource exists. A return value of true
    means the resource does not exists.

    Args:
        project_name (str): The project ID in the workspace.
        resource_name (str): The resource ID/name in the workspace.

    Returns:
        bool
    """
    try:
        get_resource_metadata(project_name, resource_name)
        return True
    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 404:
            return False
        raise error


def get_resource_response(project_name, resource_name):
    """GET resource as streamable request response.

    Args:
        project_name (str): The project ID in the workspace.
        resource_name (str): The resource ID/name in the workspace.

    Returns:
        requests.Response object
    """
    resource_url = get_resource_uri(
        project_name=project_name, resource_name=resource_name
    )
    return request(resource_url, method="GET", stream=True)


def make_new_resource(project_name, resource_name, data=None, files=None):
    """PUT create new resource.

    Args:
        project_name (str): The project ID in the workspace.
        resource_name (str): The resource ID/name in the workspace.
        data (dict): Dictionary (see requests.request) for the body
        files (dict): Dictionary (see requests.request) for multipart upload
    """
    resource_url = get_resource_uri(
        project_name=project_name, resource_name=resource_name
    )
    send_request(
        resource_url,
        method="PUT",
        data=data,
        files=files,
    )


def create_resource(project_name, resource_name, file_resource=None, replace=False):
    """Create a new resource (streamed).

    Args:
        project_name (str): The project ID in the workspace.
        resource_name (str): The resource ID/name in the workspace.
        file_resource (file stream): Already opened byte file stream
        replace (bool): Replace resource if needed.

    Returns:
        requests.Response object

    Raises:
        ValueError: missing parameter
        ValueError: Resource exist and no replace enabled
    """
    if not file_resource:
        raise ValueError("Parameter file_name is needed.")
    if not replace and resource_exist(project_name, resource_name):
        raise ValueError(
            f"Resource {resource_name} already exists " f"in project {project_name}."
        )
    resource_url = get_resource_uri(
        project_name=project_name, resource_name=resource_name
    )
    # https://requests.readthedocs.io/en/latest/user/advanced/#streaming-uploads
    with file_resource as file:
        response = request(
            resource_url,
            method="PUT",
            stream=True,
            data=file,
        )
    return response


def delete_resource(project_name, resource_name):
    """DELETE remove existing resource.

    Args:
        project_name (str): The project ID in the workspace.
        resource_name (str): The resource ID/name in the workspace.
    """
    resource_url = get_resource_uri(
        project_name=project_name, resource_name=resource_name
    )
    send_request(resource_url, method="DELETE")


def get_resource_metadata(project_name, resource_name):
    """GET retrieve resource metadata.

    Args:
        project_name (str): The project ID in the workspace.
        resource_name (str): The resource ID/name in the workspace.

    Returns:
        Depends on what json.loads gives back
    """
    resource_url = get_resource_uri(
        project_name=project_name, resource_name=resource_name, sub_path="metadata"
    )
    response = send_request(resource_url, method="GET")
    return json.loads(response.decode("utf-8"))


def get_resource_usage_data(project_name, resource_name):
    """GET retrieve the usage data of a resource.

    Args:
        project_name (str): The project ID in the workspace.
        resource_name (str): The resource ID/name in the workspace.

    Returns:
        Depends on what json.loads gives back
    """
    resource_url = get_resource_uri(
        project_name=project_name, resource_name=resource_name, sub_path="usage"
    )
    response = send_request(resource_url, method="GET")
    return json.loads(response.decode("utf-8"))
