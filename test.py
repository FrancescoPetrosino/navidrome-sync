from functions.utils import *
from functions.generals import *
from functions.search import *
from functions.playlist import *
from spotify.spotify import Spotify
import csv

NOT_FOUND_REPORT_FILE_PREFIX = './reports/not_found_songs'

def main():
    if ping_server() == -1:
        return
    
    spotify = Spotify()

    songs_to_search = []
    spotify_playlists = spotify.get_user_playlists(user_id='21ktslj6lkgx6wswmfwu5cwuq', limit=1)
    for spotify_playlist in spotify_playlists:
        spotify_playlist_tracks = spotify.get_playlist_tracks(playlist_id=spotify_playlist.get('id'))
        songs_to_search.extend(
            {"title": track.get('track', {}).get('name', ''), "artist": track.get('track', {}).get('artists', [])[0].get('name', '')}
            for track in spotify_playlist_tracks
        )

    results, not_found = search_songs_from_cache(songs_to_search)

    playlist_name = input("Enter the name of the playlist to create: ")

    create_playlist(name=playlist_name, public=False, song_ids=[s['id'] for s in results])

    with open(f"{NOT_FOUND_REPORT_FILE_PREFIX}-{spotify_playlist.get('name', 'unknown')}.csv", mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['artist', 'title'])
        writer.writeheader()
        for song in not_found:
            writer.writerow({'artist': song.get('artist', ''), 'title': song.get('title', '')})


if __name__ == "__main__":
    main()
