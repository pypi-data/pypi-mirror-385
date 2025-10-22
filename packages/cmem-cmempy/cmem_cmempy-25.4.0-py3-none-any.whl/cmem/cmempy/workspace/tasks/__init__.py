"""API for getting tasks in the data integration workspace."""

import json

from cmem.cmempy import config

from cmem.cmempy.api import send_request


def get_task_uri(project_id=None, task_id=None):
    """Get endpoint URL for the tasks API."""
    base_path = "/workspace/projects/{}/tasks"

    if project_id and task_id:
        path = base_path + "/{}"
        return config.get_di_api_endpoint() + path.format(project_id, task_id)
    return config.get_di_api_endpoint() + base_path.format(project_id)


def get_task(project=None, task=None, with_labels=True):
    """GET a task description."""
    response = send_request(
        get_task_uri(project, task) + "?withLabels=" + str(with_labels).lower(),
        method="GET",
        headers={"Accept": "application/json"},
    )
    return json.loads(response.decode("utf-8"))


def post_task(project=None, task=None, data=None, metadata=None, task_type=None):
    """POST a task"""
    if project is None:
        raise ValueError("Project name cannot be None.")
    if task is None:
        raise ValueError("Task id cannot be None.")
    if task_type is None:
        raise ValueError("Task type cannot be None.")

    url = get_task_uri(project)
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    task_data = {"id": task, "data": data or {}}

    if metadata is not None:
        task_data["metadata"] = metadata

    task_data["data"]["taskType"] = task_type

    encoded_data = json.dumps(task_data).encode("utf-8")

    response = send_request(
        url,
        method="POST",
        data=encoded_data,
        headers=headers,
    )

    return json.loads(response.decode("utf-8"))


def delete_task(project=None, task=None):
    """DELETE a task."""
    send_request(get_task_uri(project, task), method="DELETE")


def patch_parameter(project=None, task=None, data=None):
    """PATCH a task."""
    headers = {"Content-Type": "application/json"}
    data = json.dumps(data)
    send_request(
        get_task_uri(project, task), data=data, headers=headers, method="PATCH"
    )
