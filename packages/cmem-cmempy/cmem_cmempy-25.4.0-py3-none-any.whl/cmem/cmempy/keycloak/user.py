"""
API method to manage cmem realm users
"""
import json
from json import loads
from typing import Optional, Union

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_users_uri():
    """Get endpoint URI for user list."""
    path = f"/admin/realms/{config.get_keycloak_realm_id()}/users"
    return config.get_keycloak_base_uri() + path


def get_user_uri():
    """Get endpoint URI pattern for a user."""
    path = f"{get_users_uri()}/{{}}"
    return path


def get_user_group_uri():
    """Get endpoint URI pattern for a user group."""
    path = f"{get_user_groups_uri()}/{{}}"
    return path


def get_user_groups_uri():
    """Get endpoint URI pattern for a user group list."""
    path = f"{get_user_uri()}/groups"
    return path


def get_execute_actions_email_uri():
    """Get endpoint URI pattern for a execute actions email."""
    path = f"{get_user_uri()}/execute-actions-email"
    return path


def list_users(params=None):
    """List users in cmem realm."""
    uri = get_users_uri()
    list_request = send_request(uri, method="GET", params=params)
    return loads(list_request)


def request_password_change(user_id):
    """Email to update the password"""
    uri = get_execute_actions_email_uri().format(user_id)
    headers = {"Content-Type": "application/json"}
    data = ["UPDATE_PASSWORD"]
    json_data = json.dumps(data).encode("utf-8")
    send_request(uri=uri, method="PUT", headers=headers, data=json_data)


def create_user(username):
    """create user to cmem relam"""
    data = {
        "username": username,
        "email": _get_normalized_email(username),
        "enabled": True,
    }

    uri = get_users_uri()
    json_data = json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    send_request(uri, method="POST", headers=headers, data=json_data)


def _get_normalized_email(email: str) -> str:
    """validate and get normalized email.

    validation is done in a SIMPLE way and not sophisticated.
    in case the email is not valid, return an empty string.
    """
    email = email.lower().strip()
    if "@" not in email:
        return ""
    return email


def update_user(
    user_id: str,
    username: str,
    first_name: str,
    last_name: str,
    email: str,
    email_verified: Optional[bool] = None,
):
    """update user to cmem relam"""
    data: dict[str, Union[str, bool]] = {
        "username": username,
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
    }
    if email_verified is not None:
        data["emailVerified"] = email_verified
    uri = get_user_uri().format(user_id)
    json_data = json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    send_request(uri, method="PUT", headers=headers, data=json_data)


def get_user_by_username(username):
    """get user by username"""
    params = {"username": username, "exact": True}
    return list_users(params=params)


def assign_groups(user_id: str, group_ids: list):
    """assign groups to a user"""
    for group_id in group_ids:
        assign_group(user_id=user_id, group_id=group_id)


def assign_group(user_id: str, group_id):
    """assign group to a user"""
    uri = get_user_group_uri().format(user_id, group_id)
    headers = {"Content-Type": "application/json"}
    send_request(uri=uri, method="PUT", headers=headers)


def unassign_groups(user_id: str, group_ids: list):
    """unassign groups to a user"""
    for group_id in group_ids:
        unassign_group(user_id=user_id, group_id=group_id)


def unassign_group(user_id: str, group_id):
    """unassign group to a user"""
    uri = get_user_group_uri().format(user_id, group_id)
    headers = {"Content-Type": "application/json"}
    send_request(uri=uri, method="DELETE", headers=headers)


def user_groups(user_id: str):
    """List groups for a user"""
    uri = get_user_groups_uri().format(user_id)
    list_request = send_request(uri=uri, method="GET")
    return loads(list_request)


def delete_user(user_id=None):
    """delete user by id"""
    uri = get_user_uri().format(user_id)
    send_request(uri=uri, method="DELETE")


def reset_password(user_id, value, temporary=False):
    """reset user password"""
    uri = get_user_uri().format(user_id) + "/reset-password"
    data = {"type": "Password", "value": value, "temporary": temporary}
    json_data = json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    send_request(uri=uri, method="PUT", headers=headers, data=json_data)
