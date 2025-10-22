"""
API method to manage cmem realm clients
"""
from json import loads

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_clients_uri():
    """Get endpoint URI for client list."""
    path = f"/admin/realms/{config.get_keycloak_realm_id()}/clients"
    return config.get_keycloak_base_uri() + path


def get_client_uri():
    """Get endpoint URI pattern for a client."""
    path = f"{get_clients_uri()}/{{}}"
    return path


def get_client_secret_uri():
    """Get endpoint URI pattern for client-secret"""
    path = f"{get_client_uri()}/client-secret"
    return path


def list_clients(params=None):
    """List clients in cmem realm."""
    uri = get_clients_uri()
    list_request = send_request(uri, method="GET", params=params)
    return loads(list_request)


def list_open_id_clients(params=None):
    """List OAuth clients and with secret in cmem realm"""
    clients = list_clients(params=params)
    return [
        _ for _ in clients if _["protocol"] == "openid-connect" and "secret" in _.keys()
    ]


def get_client_by_client_id(client_id):
    """get client by client_id"""
    params = {"clientId": client_id}
    return list_clients(params=params)


def delete_client(client_id=None):
    """delete client"""
    uri = get_client_uri().format(client_id)
    send_request(uri=uri, method="DELETE")


def generate_client_secret(client_id=None):
    """Generate a new secret for the client"""
    uri = get_client_secret_uri().format(client_id)
    credentials = send_request(uri=uri, method="POST")
    return loads(credentials)


def get_client_secret(client_id=None):
    """Get the client secret for the client"""
    uri = get_client_secret_uri().format(client_id)
    credentials = send_request(uri=uri, method="GET")
    return loads(credentials)
