import os
from dotenv import load_dotenv
import requests
import hashlib
import random
import string
import csv
from urllib.parse import quote_plus
from functions.utils import export_list_to_csv

load_dotenv(".env")

ARTISTS_CACHE_FILE = "./cache/navidrome_artists.csv"
SONGS_CACHE_FILE = "./cache/navidrome_songs.csv"
NOT_FOUND_REPORT_FILE_PREFIX = './reports/not_found_songs'

class Navidrome:
    
    def __init__(self):
        self.server_url = os.getenv("SERVER_URL_NAVIDROME", "")
        self.username = os.getenv("USERNAME_NAVIDROME", "")
        self.password = os.getenv("PASSWORD_NAVIDROME", "")
        self.client_name = "myPythonClient"
        self.api_version = "1.16.1"
        self.format = "json"

    def __set_url__(self, url=""):
        return f"{self.get_server_url()}{url}"

    def __set_params__(self, opts=None):
        new_params = self.__get_base_params__()
        if opts:
            new_params.update(opts)
        return new_params

    def __generate_token__(self, password):
        salt = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        token = hashlib.md5((password + salt).encode()).hexdigest()
        return token, salt

    def __extract_response_data__(self, response):
        if response.status_code != 200:
            print("Request failed:", response.status_code)
            return None

        try:
            data = response.json()
            if data.get("subsonic-response", {}).get("error", None):
                print("Error in server response:", data["subsonic-response"]["error"]["message"])
                return None
            return data.get("subsonic-response", {})
        except ValueError as e:
            print("Error parsing JSON response:", e)
            return None

    def __get_base_params__(self):
        token, salt = self.__generate_token__(self.password)
        return {
            "u": self.username,
            "t": token,
            "s": salt,
            "v": self.api_version,
            "c": self.client_name,
            "f": self.format,
        }
    
    def get_server_url(self):
        if not self.server_url:
            raise ValueError("SERVER_URL_NAVIDROME is not set in the environment variables.")
        return self.server_url

    def ping_server(self) -> int:
        params = self.__get_base_params__()
        url = self.get_server_url() + "/rest/ping.view"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print("Navidrome server is reachable.")
            return 0
        else:
            print("❌ Failed to reach the Navidrome server.")
            return -1

    def get_artists(self, force_refresh=False):
        if not force_refresh and os.path.exists(ARTISTS_CACHE_FILE):
            try:
                with open(ARTISTS_CACHE_FILE, "r", encoding="utf-8", newline='') as f:
                    reader = csv.DictReader(f)
                    artist_list = list(reader)
                print(f"Cache found: {len(artist_list)} artists read from '{ARTISTS_CACHE_FILE}'")
                return artist_list
            except Exception as e:
                print(f"Error reading artist cache: {e}")

        print("Downloading all artists from Navidrome server...")

        request = requests.get(self.__set_url__("/rest/getArtists.view"), params=self.__set_params__())
        request.raise_for_status()
        artists_data = request.json()["subsonic-response"]["artists"]
        artist_list = []

        for group in artists_data.get("index", []):
            artist_list.extend(group.get("artist", []))

        # Only keep Name and Id
        filtered_artists = [{"id": a["id"], "name": a["name"]} for a in artist_list if "id" in a and "name" in a]

        try:
            os.makedirs(os.path.dirname(ARTISTS_CACHE_FILE), exist_ok=True)
            export_list_to_csv(
                data=filtered_artists,
                file_path=ARTISTS_CACHE_FILE,
                fieldnames=["id", "name"]
            )
        except Exception as e:
            print(f"Error saving artist cache: {e}")

        return filtered_artists

    def get_albums_by_artist(self, artist_id):
        params = self.__set_params__({
            "id": artist_id
        })
        r = requests.get(self.__set_url__("/rest/getArtist.view"), params=params)
        r.raise_for_status()
        return r.json()["subsonic-response"]["artist"].get("album", [])

    def get_songs_by_album(self, album_id):
        params = self.__set_params__({
            "id": album_id
        })
        r = requests.get(self.__set_url__("/rest/getAlbum.view"), params=params)
        r.raise_for_status()
        return r.json()["subsonic-response"]["album"].get("song", [])

    def fetch_all_songs(self, force_refresh=False):
        if not force_refresh and os.path.exists(SONGS_CACHE_FILE):
            try:
                cached_songs = []
                with open(SONGS_CACHE_FILE, "r", encoding="utf-8", newline='') as f:
                    reader = csv.DictReader(f)
                    cached_songs = list(reader)
                print(f"📁 Cache trovata: {len(cached_songs)} brani letti da '{SONGS_CACHE_FILE}'")
                return cached_songs
            except Exception as e:
                print(f"Error reading cache: {e}")

        print("Fetching data...")

        artist_list = self.get_artists(force_refresh=force_refresh)
        all_songs = []

        progress_artist = 0
        total_artists = len(artist_list)

        for artist in artist_list:
            progress_artist += 1
            print(f"Caching data progress {progress_artist * 100 // total_artists}% take {progress_artist} coffee ☕")
            albums = self.get_albums_by_artist(artist["id"])
            if not albums:
                print(f"No albums found for artist: {artist['name']}")
                continue
            else:
                for album in albums:
                    songs = self.get_songs_by_album(album["id"])
                    if not songs:
                        print(f"No songs found for album: {album['name']} by {artist['name']}")
                        continue
                    else:
                        all_songs.extend(songs)

        print(f"Completed: {len(all_songs)} brani trovati.")
        
        if not all_songs:
            print("No songs found in the library.")
            return []

        try:
            os.makedirs(os.path.dirname(SONGS_CACHE_FILE), exist_ok=True)
            
            filtered_songs = [
                {"id": s["id"], "title": s["title"], "artist": s["artist"], "artist_id": s["artistId"], "album": s["album"], "album_id": s["albumId"]}
                for s in all_songs if "id" in s and "title" in s
            ]

            all_keys = set()
            for song in filtered_songs:
                all_keys.update(song.keys())
            
            fieldnames = sorted(list(all_keys))
            
            export_list_to_csv(
                data=filtered_songs,
                file_path=SONGS_CACHE_FILE,
                fieldnames=fieldnames
            )
            print(f"Cache updated with {len(filtered_songs)} songs in '{SONGS_CACHE_FILE}'")
        except Exception as e:
            print(f"Error saving cache: {e}")

        return filtered_songs

    def search_songs_from_cache(self, songs_to_search=[]):
        if not os.path.exists(SONGS_CACHE_FILE):
            print(f"Cache file '{SONGS_CACHE_FILE}' does not exist. Please fetch songs first.")
            self.fetch_all_songs(force_refresh=True)
        
        try:
            with open(SONGS_CACHE_FILE, "r", encoding="utf-8", newline='') as f:
                reader = csv.DictReader(f)
                cached_songs = list(reader)
        except Exception as e:
            print(f"Error reading cache: {e}")
            return []

        matched_songs = []
        not_found_songs = []

        for song in songs_to_search:
            title = song.get("title", "")
            artist = song.get("artist", "")
            matches = [
                song for song in cached_songs
                if title.lower() in song.get('title', '').lower()
                and artist.lower() in song.get('artist', '').lower()
            ]
            if matches:
                print(f"✅ Found {len(matches)} matches for '{title}' by '{artist}'")
                matched_songs.extend(matches)
            else:
                print(f"❌ No matches found for '{title}' by '{artist}'")
                not_found_songs.append(song)

        return matched_songs, not_found_songs
    
    def get_all_playlists(self):
        params = self.__set_params__()
        url = self.__set_url__("/rest/getPlaylists.view")
        response = requests.get(url, params=params)
        data = self.__extract_response_data__(response)
        if data:
            for playlist in data.get("playlists", {}).get("playlist", []):
                print(f"Playlist: {playlist['name']} (ID: {playlist['id']}) - Number of songs: {playlist.get('songCount', 0)} Owner: {playlist.get('owner', 'Unknown')}")
        else:
            print("No playlists found or an error occurred.")

    def create_playlist(self, name="", public=False, song_ids=[]):
        if not name or not song_ids:
            print("Name and song IDs are required to create a playlist.")
            return
        params = self.__set_params__({
            "name": name,
            "public": str(public).lower(),
        })
        for song_id in song_ids:
            params.setdefault("songId", []).append(quote_plus(str(song_id)))
        url = self.__set_url__("/rest/createPlaylist.view")
        response = requests.post(url, params=params)
        data = self.__extract_response_data__(response)
        if data and data.get("playlist", None) is not None:
            print(f"✅ Playlist '{name}' created successfully with {len(song_ids)} songs.")
        else:
            print("❌ Failed to create playlist or an error occurred.")

    def delete_playlist(self, playlist_id):
        if not playlist_id:
            print("Playlist ID is required to delete a playlist.")
            return
        params = self.__set_params__({
            "id": playlist_id,
        })
        url = self.__set_url__("/rest/deletePlaylist.view")
        response = requests.post(url, params=params)
        data = self.__extract_response_data__(response)
        if data and data.get("status", None) == "ok":
            print(f"Playlist with ID '{playlist_id}' deleted successfully.")
        else:
            print("Failed to delete playlist or an error occurred.")

    def add_songs_to_playlist(self, playlist_id, song_ids):
        if not playlist_id or not song_ids:
            print("Playlist ID and song IDs are required to add songs to a playlist.")
            return
        params = self.__set_params__({
            "playlistId": playlist_id,
        })
        for song_id in song_ids:
            params.setdefault("songIdToAdd", []).append(quote_plus(str(song_id)))
        url = self.__set_url__("/rest/updatePlaylist.view")
        response = requests.post(url, params=params)
        data = self.__extract_response_data__(response)
        if data and data.get("status", None) == "ok":
            print(f"Songs added to playlist with ID '{playlist_id}' successfully.")
        else:
            print("Failed to add songs to playlist or an error occurred.")