import requests
from functions.utils import *

def ping_server() -> int:
    params = set_params()
    url = set_url("/rest/ping.view")
    response = requests.get(url, params=params)
    data = extract_response_data(response)
    if data:
        print("Navidrome server is reachable.")
        return 0
    else:
        print("❌ Failed to reach the Navidrome server.")
        return -1