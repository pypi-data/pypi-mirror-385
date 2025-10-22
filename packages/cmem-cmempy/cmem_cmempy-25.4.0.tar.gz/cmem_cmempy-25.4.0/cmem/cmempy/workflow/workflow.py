"""API methods for working with a single workflow."""
from requests_toolbelt.multipart import encoder
from cmem.cmempy import config
from cmem.cmempy.api import get_json, request, send_request
from cmem.cmempy.workspace.tasks import post_task


def get_workflow_uri():
    """Get endpoint URI pattern for a workflow."""
    return config.get_di_api_endpoint() + "/workflow/workflows/{}/{}"


def get_workflow_execute_uri():
    """Get execute URI pattern for a workflow."""
    return get_workflow_uri() + "/execute"


def get_workflow_status_uri():
    """Get status URI pattern for a workflow."""
    return get_workflow_uri() + "/status"


def get_workflow_execute_on_payload_uri():
    """Get execute on payload URI pattern for a workflow."""
    return get_workflow_uri() + "/executeOnPayload"


def get_workflow_editor_uri():
    """Get execute URI pattern for a workflow.

    Since 21.01 this is changed to the new workbench
    """
    return config.get_di_api_endpoint() + "/workbench/projects/{}/workflow/{}"


def get_workflow(project_name, task_name):
    """GET retrieve single workflow."""
    return send_request(
        get_workflow_uri().format(project_name, task_name), method="GET"
    ).decode("utf-8")


def make_new_workflow(project_name, task_name, data=None, metadata=None):
    """PUT create workflow."""
    return post_task(
        project=project_name,
        task=task_name,
        data=data,
        metadata=metadata,
        task_type="Workflow",
    )


def execute_on_payload(project_name, task_name, data=None, headers=None):
    """POST execute on payload."""
    if not headers:
        headers = {"Content-Type": "application/xml"}

    # pylint: disable-msg=duplicate-code
    return send_request(
        get_workflow_execute_on_payload_uri().format(project_name, task_name),
        method="POST",
        data=data,
        headers=headers,
    ).decode("utf-8")


def delete_workflow(project_name, task_name):
    """DELETE remove workflow."""
    return send_request(
        get_workflow_uri().format(project_name, task_name), method="DELETE"
    ).decode("utf-8")


def execute_workflow(project_name, task_name):
    """PUT execute workflow."""
    return send_request(
        get_workflow_execute_uri().format(project_name, task_name), method="PUT"
    ).decode("utf-8")


def get_workflow_status(project_name, task_name):
    """GET workflow status.

    Returns gibberish, internal API endpoint
    use cmempy.workspace.activities.taskactivities.get_activity_status
    instead
    """
    return send_request(
        get_workflow_status_uri().format(project_name, task_name), method="GET"
    ).decode("utf-8")


def get_workflows_io():
    """Get a list of suitable io workflow incl. input/output information.

    see CMEM-3089

    Args:
        project_name: project ID

    Returns:
        list of dicts of workflow infos
    """
    endpoint = f"{config.get_di_api_endpoint()}/api/workflow/info"
    params = {}
    io_workflows = []
    for _ in get_json(endpoint, method="GET", params=params):
        ins = len(_["variableInputs"])
        outs = len(_["variableOutputs"])
        if ins == 1 or outs == 1:
            io_workflows.append(_)
    return io_workflows


# pylint: disable=too-many-arguments
def execute_workflow_io(
    project_name,
    task_name,
    input_file=None,
    input_mime_type="application/xml",
    output_mime_type="application/xml",
    auto_config=False,
):
    """Execute a workflow with variable input or output from or to a file.

    see CMEM-3089

    Args:
        project_name: project ID
        task_name: workflow ID
        input_file: file path
        input_mime_type: A mime type string
        output_mime_type: A mime type string
        auto_config (bool): enable autoconfiguration of input dataset

    Returns:
        Response object from requests API
    """
    endpoint = (
        f"{config.get_di_api_endpoint()}/api/workflow/"
        f"result/{project_name}/{task_name}"
    )

    if auto_config:
        endpoint = f"{endpoint}?config-general-autoConfig=true"
    headers = {"Accept": output_mime_type}
    if input_file and input_mime_type:
        # in case an input is given, do a streaming upload
        headers["Content-Type"] = input_mime_type
        with open(input_file, "rb") as data:
            files = [("file", (input_file, data, input_mime_type))]
            multipart_encoder = encoder.MultipartEncoder(fields=files)
            headers["Content-Type"] = multipart_encoder.content_type
            return request(
                endpoint,
                method="POST",
                headers=headers,
                data=multipart_encoder,
                stream=True,
            )
    # without an input, just a post without a body - needed for only output requests
    return request(endpoint, method="POST", headers=headers, stream=True)
