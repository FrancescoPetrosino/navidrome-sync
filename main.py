from functions.utils import *
from functions.generals import *
from functions.search import *
from functions.playlist import *

def main():
    if ping_server() == -1:
        return
    # query = input("Cerca una canzone: ")
    # search_music(query)
    get_all_playlists()


if __name__ == "__main__":
    main()
