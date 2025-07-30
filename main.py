from functions.utils import *
from functions.generals import *
from functions.search import *
from functions.playlist import *

def main():
    if ping_server() == -1:
        return
    # query = input("Cerca una canzone: ")
    # search_music(query)
    # create_playlist(name="My Playlist 4", public=False, song_ids=[
    #     "434adc02680ad5241a2f0da3a36f9b8a",
    #     "bffc7f470424c1597fb7933051e4b19d"
    # ])
    # delete_playlist(playlist_id="E3qucnidoHfQeIBlC3g0ys")
    # add_songs_to_playlist(playlist_id="mEndSi4wSbgxEQGO08MTnU", song_ids=[
    #     "434adc02680ad5241a2f0da3a36f9b8a",
    #     "bffc7f470424c1597fb7933051e4b19d"
    # ])
    get_all_playlists()


if __name__ == "__main__":
    main()
