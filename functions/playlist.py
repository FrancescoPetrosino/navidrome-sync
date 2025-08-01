import requests
from functions.utils import *
from urllib.parse import quote_plus

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

def create_playlist(name="", public=False, song_ids=[]):
    if not name or not song_ids:
        print("Name and song IDs are required to create a playlist.")
        return
    params = set_params({
        "name": name,
        "public": str(public).lower(),
    })
    for song_id in song_ids:
        params.setdefault("songId", []).append(quote_plus(str(song_id)))
    url = set_url("/rest/createPlaylist.view")
    response = requests.post(url, params=params)
    data = extract_response_data(response)
    if data and data.get("playlist", None) is not None:
        print(f"✅ Playlist '{name}' created successfully with {len(song_ids)} songs.")
    else:
        print("❌ Failed to create playlist or an error occurred.")

def delete_playlist(playlist_id):
    if not playlist_id:
        print("Playlist ID is required to delete a playlist.")
        return
    params = set_params({
        "id": playlist_id,
    })
    url = set_url("/rest/deletePlaylist.view")
    response = requests.post(url, params=params)
    data = extract_response_data(response)
    if data and data.get("status", None) == "ok":
        print(f"Playlist with ID '{playlist_id}' deleted successfully.")
    else:
        print("Failed to delete playlist or an error occurred.")

def add_songs_to_playlist(playlist_id, song_ids):
    if not playlist_id or not song_ids:
        print("Playlist ID and song IDs are required to add songs to a playlist.")
        return
    params = set_params({
        "playlistId": playlist_id,
    })
    for song_id in song_ids:
        params.setdefault("songIdToAdd", []).append(quote_plus(str(song_id)))
    url = set_url("/rest/updatePlaylist.view")
    response = requests.post(url, params=params)
    data = extract_response_data(response)
    if data and data.get("status", None) == "ok":
        print(f"Songs added to playlist with ID '{playlist_id}' successfully.")
    else:
        print("Failed to add songs to playlist or an error occurred.")