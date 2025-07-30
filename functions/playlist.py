import requests
from functions.utils import *

def get_all_playlists():
    params = set_params()
    url = set_url("/rest/getPlaylists.view")
    response = requests.get(url, params=params)
    data = extract_response_data(response)
    if data:
        for playlist in data.get("playlists", {}).get("playlist", []):
            print(f"Playlist: {playlist['name']} (ID: {playlist['id']}) - Number of songs: {playlist.get('songCount', 0)} Owner: {playlist.get('owner', 'Unknown')}")
    else:
        print("No playlists found or an error occurred.")