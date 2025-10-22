"""API for health and version information."""
import json
import re

from requests import HTTPError

from cmem.cmempy import config
from cmem.cmempy.api import get_json, send_request
from cmem.cmempy.queries import SparqlQuery

SHAPE_CATALOG_VERSION_QUERY = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <https://vocab.eccenca.com/shacl/>
SELECT ?version
FROM :
WHERE {
  : owl:versionInfo ?version
}
ORDER BY ASC(?version)
"""


def get_explore_health_endpoint():
    """Get explore health endpoint."""
    return get_dp_health_endpoint()


def get_dp_health_endpoint():
    """Get DataPlatform health endpoint."""
    return config.get_dp_api_endpoint() + "/actuator/health"


def get_dp_info_endpoint():
    """Get DataPlatform version endpoint."""
    return config.get_dp_api_endpoint() + "/actuator/info"


def get_di_health_endpoint():
    """Get DataPlatform health endpoint."""
    return config.get_di_api_endpoint() + "/health"


def get_di_version_endpoint():
    """Get DataPlatform version endpoint."""
    return config.get_di_api_endpoint() + "/version"


def get_dm_version_endpoint():
    """Get DataManager version endpoint."""
    return config.get_cmem_base_uri() + "/version.html"


def get_shape_catalog_version():
    """GET version of the ShapeCatalog."""
    try:
        results = SparqlQuery(SHAPE_CATALOG_VERSION_QUERY).get_json_results()[
            "results"
        ]["bindings"]
        if len(results) > 0:
            return str(results[0]["version"]["value"])
    except (KeyError, HTTPError):
        pass
    return "UNKNOWN"


def get_dm_version():
    """GET version of DataManager."""
    url = get_dm_version_endpoint()
    try:
        response = send_request(url).decode()
    except HTTPError:
        return "ERROR"
    try:
        response = re.findall(r"v[0-9]+\..*", response)[0]
        return response
    except Exception:  # pylint: disable=broad-except
        return "UNKNOWN"


def get_explore_version():
    """GET version of Explore."""
    return get_dp_version()


def get_dp_version():
    """GET version of DataPlatform."""
    response = None
    url = get_dp_info_endpoint()
    try:
        response = send_request(url)
    except Exception:  # pylint: disable=broad-except
        response = None
        # TODO: checking health status needs to be improved
    if response is None:
        url = url.replace("/actuator", "")
        response = send_request(url)
    result = json.loads(response)
    return result["version"]


def dp_is_healthy():
    """Check status of DataIntegration."""
    url = get_dp_health_endpoint()
    try:
        response = send_request(url)
    except Exception:  # pylint: disable=broad-except
        response = None
        # TODO: checking health status needs to be improved
    if response is None:
        url = url.replace("/actuator", "")
        response = send_request(url)
    result = json.loads(response)
    if result["status"] == "UP":
        return True
    return False


def get_di_version():
    """GET version of DataIntegration."""
    response = send_request(get_di_version_endpoint())
    return response.decode("utf-8")


def di_is_healthy():
    """Check status of DataIntegration."""
    try:
        result = json.loads(send_request(get_di_health_endpoint()))
    except ValueError:
        return False
    if result["status"] == "UP":
        return True
    return False


def get_complete_status_info() -> dict:
    """Collect all status info and provide proper dictionary."""
    info = {
        "build": {"version": "UNKNOWN", "healthy": "UNKNOWN"},
        "explore": {"version": "UNKNOWN", "healthy": "UNKNOWN"},
        "shapes": {"version": "UNKNOWN", "healthy": "UNKNOWN"},
        "store": {"type": "STORE", "version": "UNKNOWN", "healthy": "UNKNOWN"},
    }
    e_prefix = "Error: "
    try:
        info["build"]["version"] = get_di_version()
        info["build"]["healthy"] = "UP" if di_is_healthy() else "DOWN"
    except Exception as error:  # pylint: disable=broad-except
        info["build"]["error"] = f"{e_prefix}{error}"
        info["build"]["healthy"] = "DOWN"
    try:
        info["explore"]["info"] = get_explore_info()  # type: ignore
        info["explore"]["health"] = get_json(get_explore_health_endpoint())
        info["explore"]["version"] = info["explore"]["info"]["version"]  # type: ignore
        info["explore"]["healthy"] = info["explore"]["health"]["status"]  # type: ignore
        if "store" in info["explore"]["info"]:
            info["store"]["type"] =\
                info["explore"]["info"]["store"]["type"]  # type: ignore
            # fmt: off
            info["store"]["version"] = (
                info["explore"]["info"]["store"]["version"]  # type: ignore
            )
            # fmt: on
        info["store"]["healthy"] = info["explore"]["healthy"]
    except Exception as error:  # pylint: disable=broad-except
        info["explore"]["error"] = f"{e_prefix}{error}"
        info["explore"]["healthy"] = "DOWN"
    try:
        info["shapes"]["version"] = get_shape_catalog_version()
        if info["shapes"]["version"] == "UNKNOWN":
            info["shapes"]["healthy"] = "DOWN"
        else:
            info["shapes"]["healthy"] = "UP"
    except Exception as error:  # pylint: disable=broad-except
        info["shapes"]["error"] = f"{e_prefix}{error}"
    # combine overall.status
    info["overall"] = {
        "healthy": "UP" if all(
            component["healthy"] == "UP" for component in info.values()
        ) else "DOWN"
    }
    return info


def get_explore_info() -> dict:
    """Get explore info."""
    return get_dp_info()


def get_dp_info() -> dict:
    """Get dp health info."""
    return dict(get_json(get_dp_info_endpoint()))
