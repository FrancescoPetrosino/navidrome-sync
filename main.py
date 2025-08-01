from navidrome.navidrome import Navidrome
from spotify.spotify import Spotify
from functions.utils import export_list_to_csv

NOT_FOUND_REPORT_FILE_PREFIX = './reports/not_found_songs'

def main():
    navidrome = Navidrome()
    if navidrome.ping_server() == -1:
        return
    
    spotify = Spotify()

    songs_to_search = []
    spotify_playlists = spotify.get_user_playlists(user_id='21ktslj6lkgx6wswmfwu5cwuq')

    print("\nChoose a playlist to sync from the following Spotify playlists:")
    i = 1
    for spotify_playlist in spotify_playlists:
        print(f"{i} - {spotify_playlist.get('name', 'Unknown')}")
        i += 1

    choice_playlist_number = input("Enter the number of the playlist to sync: ")
    if not choice_playlist_number.isdigit() or int(choice_playlist_number) < 1 or int(choice_playlist_number) > len(spotify_playlists):
        print("Invalid choice. Exiting.")
        return

    spotify_playlist_tracks = spotify.get_playlist_tracks(playlist_id=spotify_playlists[int(choice_playlist_number) - 1].get('id'))
    songs_to_search.extend(
        {"title": track.get('track', {}).get('name', ''), "artist": track.get('track', {}).get('artists', [])[0].get('name', '')}
        for track in spotify_playlist_tracks
    )

    results, not_found = navidrome.search_songs_from_cache(songs_to_search=songs_to_search)

    print("")
    choice_playlist_name = input("Would you enter a different name for the Navidrome playlist? (y/n): ")
    if choice_playlist_name.lower() == 'y':
        choice_playlist_name = input("Enter the new name for the Navidrome playlist: ")
    else:
        choice_playlist_name = spotify_playlists[int(choice_playlist_number) - 1].get('name', 'Unknown')
    print("\n")
    
    navidrome.create_playlist(
        name=choice_playlist_name,
        public=False, 
        song_ids=[s['id'] for s in results]
    )

    not_found.sort(key=lambda x: (x['artist'], x['title']))
    if not_found:
        print("The following songs were not found in Navidrome and will not be added to the playlist")
        export_file_path = f"{NOT_FOUND_REPORT_FILE_PREFIX}-{spotify_playlists[int(choice_playlist_number) - 1].get('name', 'Unknown')}.csv"
        export_list_to_csv(
            data=not_found,
            file_path=export_file_path,
            fieldnames=['artist', 'title']
        )
        print(f"You can find the report in the reports folder {export_file_path}")


if __name__ == "__main__":
    main()
