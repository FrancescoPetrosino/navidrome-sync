from spotify import Spotify

def main():
    spotify = Spotify()
    
    playlists = spotify.get_user_playlists(user_id='21ktslj6lkgx6wswmfwu5cwuq')
    
    for playlist in playlists.get('items', []):
        spotify.get_playlist_tracks(playlist_id=playlist.get('id'))


if __name__ == "__main__":
    main()