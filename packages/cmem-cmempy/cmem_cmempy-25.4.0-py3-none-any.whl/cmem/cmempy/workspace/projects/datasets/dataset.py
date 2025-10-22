"""API methods for working with single datasets."""
import json

from requests_toolbelt.multipart.encoder import MultipartEncoder

from cmem.cmempy import config
from cmem.cmempy.api import send_request, request


def get_dataset_uri():
    """Get endpoint URI pattern for a dataset."""
    path = "/workspace/projects/{}/datasets/{}"
    return config.get_di_api_endpoint() + path


def get_dataset_file_uri():
    """Get the endpoint URI for a dataset file."""
    return get_dataset_uri() + "/file"


def get_dataset(project_name, dataset_name):
    """GET retrieve single dataset."""
    headers = {"Accept": "application/json"}
    response = send_request(
        get_dataset_uri().format(project_name, dataset_name),
        method="GET",
        headers=headers,
    )
    return json.loads(response.decode("utf-8"))


def make_new_dataset(
    project_name, dataset_name, dataset_type, parameters, autoconfigure
):
    """PUT create new dataset (deprecated)."""
    data = {
        "id": f"{dataset_name}",
        "type": f"{dataset_type}",
        "parameters": parameters,
    }
    data = json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    params = None
    if autoconfigure:
        params = {"autoConfigure": "true"}
    send_request(
        get_dataset_uri().format(project_name, dataset_name),
        method="PUT",
        data=data,
        headers=headers,
        params=params,
    )


def delete_dataset(project_name, dataset_name):
    """DELETE remove existing dataset."""
    send_request(get_dataset_uri().format(project_name, dataset_name), method="DELETE")


# pylint: disable=too-many-arguments
def create_dataset(
    project_id,
    dataset_type,
    dataset_id=None,
    parameter=None,
    metadata=None,
    read_only=False,
    uri_property=None,
):
    """Create a dataset.

    In difference to make_new_dataset, this uses the task API and does
    not enforce an ID in advance. Also, it allows for metadata parameters.
    """
    if parameter is None:
        parameter = {}
    if metadata is None:
        metadata = {}
    # add needed base task data
    data = {
        "taskType": "Dataset",
        "type": dataset_type,
        "parameters": parameter,
        "metadata": metadata,
        "readOnly": read_only,
        "uriProperty": uri_property,
    }
    # add the optional task / dataset ID
    if dataset_id:
        data["id"] = dataset_id
    params = None
    path = f"/workspace/projects/{project_id}/tasks"
    return send_request(
        config.get_di_api_endpoint() + path,
        method="POST",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        params=params,
    )


def post_resource(project_id, dataset_id, file_resource=None, resource_url=None):
    """
    Post a resource to a dataset.

    If the dataset resource already exists, posting a new resource will replace it.

    Args:
        project_id (str): The ID of the project.
        dataset_id (str): The ID of the dataset.
        file_resource (io Binary Object, optional): The file resource to be uploaded.
        resource_url (str, optional): The URL of the resource to be uploaded.

    Returns:
        Response: The response from the request.

    """

    if not file_resource and not resource_url:
        raise ValueError("Parameter file_resource or resource_url is needed.")

    endpoint = get_dataset_file_uri().format(project_id, dataset_id)
    if file_resource:
        with file_resource as file:
            response = request(
                endpoint,
                method="PUT",
                stream=True,
                data=file,
            )
        return response

    multipart_encoder = MultipartEncoder(fields=[("resource-url", resource_url)])
    headers = {"Content-Type": multipart_encoder.content_type}
    return request(
        endpoint,
        method="PUT",
        headers=headers,
        data=multipart_encoder,
        stream=True,
    )


def get_resource(project_id, dataset_id):
    """Get a resource"""
    endpoint = get_dataset_file_uri().format(project_id, dataset_id)
    response = send_request(
        endpoint,
        method="GET",
    )
    return response.decode("utf-8")


def update_dataset(
    project_id,
    dataset_id,
    parameters=None,
    metadata=None,
    read_only=False,
    uri_property=None,
):
    """Update a dataset"""
    if parameters is None:
        parameters = {}
    if metadata is None:
        metadata = {}
    data = {
        "metadata": metadata,
        "data": {
            "readOnly": read_only,
            "uriProperty": uri_property,
            "parameters": parameters,
        },
    }
    path = f"/workspace/projects/{project_id}/tasks/{dataset_id}"
    return send_request(
        config.get_di_api_endpoint() + path,
        method="PATCH",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
