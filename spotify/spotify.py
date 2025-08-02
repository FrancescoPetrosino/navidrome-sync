import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import csv
from functions.utils import export_list_to_csv

load_dotenv(".env")

PLAYLIST_CACHE_FILE = "./cache/spotify_playlist_cache.csv"

class Spotify:
    __sp = None
    __scope = [
        "user-library-read",
        "user-top-read",
        "user-follow-read",
        "user-read-private",
        "user-read-email",
        "user-read-recently-played",
        "user-read-playback-state",
        "user-modify-playback-state",
        "user-read-playback-position",
        "streaming",
        "app-remote-control",
        "playlist-read-private",
        "playlist-modify-private",
        "playlist-modify-public",
        "playlist-read-collaborative"
    ]

    def __init__(self):
        self.__client_id = os.getenv("SPOTIFY_CLIENT_ID", "")
        self.__client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "")
        self.__user_id = os.getenv("SPOTIFY_USER_ID", "")
        self.__redirect_uri = "http://localhost:8080"
        self.get_auth()
        self.get_current_user()
    
    def get_auth(self):
        auth_manager = SpotifyOAuth(
            client_id=self.__client_id,
            client_secret=self.__client_secret,
            redirect_uri=self.__redirect_uri,
            scope=self.__scope
        )
        self.__sp = spotipy.Spotify(auth_manager=auth_manager)

    def get_current_user(self):
        print("You are logged in with user id: " + self.__user_id)
        return self.__user_id

    def get_user_playlists(self, user_id=None, limit=50, force_refresh=False, silent=True):
        if user_id is None:
            user_id = self.__user_id

        if not force_refresh and os.path.exists(PLAYLIST_CACHE_FILE):
            with open(PLAYLIST_CACHE_FILE, 'r', encoding='utf-8', newline='') as f:
                playlists = csv.DictReader(f)
                playlists = list(playlists)
            if not silent:
                for playlist in playlists:
                    print(f"Playlist: {playlist.get('name')} (ID: {playlist.get('id')}) - Number of songs: {playlist.get('tracks', {}).get('total', 0)} Owner: {playlist.get('owner', {}).get('display_name', 'Unknown')} - Public: {playlist.get('public', False)}")
            return playlists
        
        current_response_counter = limit
        offset = 0
        playlists = []
        while current_response_counter > 0:
            result = self.__sp.user_playlists(
                user=user_id,
                offset=offset,
                limit=limit
            )
            playlists.extend(result.get('items', []))
            current_response_counter = len(result.get('items', []))
            offset += limit
        if not silent:
            for playlist in playlists:
                print(f"Playlist: {playlist.get('name')} (ID: {playlist.get('id')}) - Number of songs: {playlist.get('tracks', {}).get('total', 0)} Owner: {playlist.get('owner', {}).get('display_name', 'Unknown')} - Public: {playlist.get('public', False)}")
        
        filtered_playlists = [
            {
                'id': playlist.get('id', 'Unknown'),
                'name': playlist.get('name', 'Unknown'),
                'tracks_number': playlist.get('tracks', {}).get('total', 0),
                'owner': playlist.get('owner', {}).get('display_name', 'Unknown'),
                'public': playlist.get('public', False)
            } for playlist in playlists
        ]

        try:
            os.makedirs(os.path.dirname(PLAYLIST_CACHE_FILE), exist_ok=True)
            export_list_to_csv(
                data=filtered_playlists,
                file_path=PLAYLIST_CACHE_FILE,
                fieldnames=['id', 'name', 'tracks_number', 'owner', 'public']
            )
            print(f"Cache updated with {len(filtered_playlists)} playlists in '{PLAYLIST_CACHE_FILE}'")
        except Exception as e:
            print(f"Error saving playlist cache: {e}")

        return filtered_playlists

    def get_playlist_tracks(self, playlist_id, limit=50, silent=True):
        if playlist_id is None:
            print("Playlist ID is required to get tracks.")
            return []
        current_response_counter = limit
        offset = 0
        tracks = []
        while current_response_counter > 0:
            result = self.__sp.playlist_tracks(
                playlist_id=playlist_id,
                offset=offset,
                limit=limit
            )
            tracks.extend(result.get('items', []))
            current_response_counter = len(result.get('items', []))
            offset += limit
        for item in tracks:
            track = item.get('track', None)
            if track and not silent:
                print(f"Track: {track.get('name')} by {', '.join(artist['name'] for artist in track.get('artists', []))} (ID: {track.get('id', 'Unknown')})")
        return tracks