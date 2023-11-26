import requests
import json


def get_remote_version() -> str:
    """Gets the latest version of slh-sh from pypi.org

    Returns:
        str: latest version
    """
    url = "https://pypi.org/pypi/slh-sh/json"

    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.content.decode("utf-8"))
        return data["info"]["version"]
    else:
        return "An error occurred while retrieving the package version."
