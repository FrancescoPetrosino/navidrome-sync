import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv("../.env")

SPOTIFY_CLIENT_ID=os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET=os.getenv("SPOTIFY_CLIENT_SECRET", "")
REDIRECT_URI='http://localhost:8080'

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
        self.get_auth()
        self.get_current_user()
    
    def get_auth(self):
        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=self.__scope
        )
        self.__sp = spotipy.Spotify(auth_manager=auth_manager)

    def get_current_user(self):
        print("Connected as: " + self.__sp.current_user().get('display_name', 'Error!'))

    def get_user_playlists(self, user_id=None, limit=50, silent=True):
        if user_id is None:
            user_id = self.__sp.current_user()['id']
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
        return playlists

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