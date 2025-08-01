from spotify import Spotify

def main():
    spotify = Spotify()
    
    playlists = spotify.get_user_playlists(user_id='21ktslj6lkgx6wswmfwu5cwuq', limit=1, silent=False)
    
    for playlist in playlists:
        spotify.get_playlist_tracks(playlist_id=playlist.get('id'), limit=20, silent=False)


if __name__ == "__main__":
    main()