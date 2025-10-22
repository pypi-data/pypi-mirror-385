"""
API method to manage cmem realm groups
"""
from json import loads

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_groups_uri():
    """Get endpoint URI for group list."""
    path = f"/admin/realms/{config.get_keycloak_realm_id()}/groups"
    return config.get_keycloak_base_uri() + path


def list_groups(params=None):
    """List groups in cmem relam"""
    uri = get_groups_uri()
    list_request = send_request(uri, method="GET", params=params)
    return loads(list_request)
