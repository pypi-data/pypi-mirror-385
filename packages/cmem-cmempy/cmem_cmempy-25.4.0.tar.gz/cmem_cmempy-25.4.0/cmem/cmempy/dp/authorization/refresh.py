"""API for refreshing access conditions in DP."""

from cmem.cmempy import config

from cmem.cmempy.api import request


def get_authorization_refresh_uri():
    """Get endpoint URI for the authorization refresh."""
    return config.get_dp_api_endpoint() + "/authorization/refresh"


AUTHORIZATION_GRAPH_URI = "https://ns.eccenca.com/data/ac/"


def get():
    """GET -> Refresh access conditions."""
    return request(get_authorization_refresh_uri(), method="GET")
