from functions.utils import *
from functions.generals import *
from functions.search import *
from functions.playlist import *
from spotify.spotify import Spotify

def main():
    if ping_server() == -1:
        return
    
    # spotify = Spotify()
    
    songs = fetch_all_songs(force_refresh=True)
    print(f"Total songs fetched: {len(songs)}")
    
    # create_playlist(name="My Playlist 4", public=False, song_ids=[
    #     "434adc02680ad5241a2f0da3a36f9b8a",
    #     "bffc7f470424c1597fb7933051e4b19d"
    # ])
    # delete_playlist(playlist_id="E3qucnidoHfQeIBlC3g0ys")
    # add_songs_to_playlist(playlist_id="mEndSi4wSbgxEQGO08MTnU", song_ids=[
    #     "434adc02680ad5241a2f0da3a36f9b8a",
    #     "bffc7f470424c1597fb7933051e4b19d"
    # ])
    
    #navidrome_playlists = get_all_playlists()
    # spotify_playlists = spotify.get_user_playlists(user_id='21ktslj6lkgx6wswmfwu5cwuq')

    # for spotify_playlist in spotify_playlists.get('items', []):
    #     spotify_playlist_tracks = spotify.get_playlist_tracks(playlist_id=spotify_playlist.get('id'))
    #     for spotify_track in spotify_playlist_tracks.get('items', []):
    #         navidrome_songs = search_music(query=spotify_track.get('track', {}).get('name', ''), limit=1)

if __name__ == "__main__":
    main()
