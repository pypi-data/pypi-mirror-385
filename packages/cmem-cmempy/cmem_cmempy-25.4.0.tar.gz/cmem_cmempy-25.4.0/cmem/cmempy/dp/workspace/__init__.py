"""API methods for working with workspace configurations."""
from cmem.cmempy import config
from cmem.cmempy.api import get_json


def get_workspaces_uri():
    """Get the endpoint URI for a workspaces."""
    return f"{config.get_dp_api_endpoint()}/api/conf/workspaces"


def get_workspace_migrate_uri():
    """Get the endpoint URI for a workspace migration."""
    return f"{get_workspaces_uri()}/migrateConfiguration"


def migrate_workspaces():
    """Migrate workspaces."""
    return get_json(
        uri=get_workspace_migrate_uri(),
        method="POST",
    )
