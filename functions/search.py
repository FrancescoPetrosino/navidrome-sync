import requests
from functions.utils import *

def search_music(query, search_type="song", limit=10):
    params = set_params({
        "query": query,
        "type": search_type,
        "songCount": limit,
    })
    url = set_url("/rest/search2.view")
    response = requests.get(url, params=params)

    data = extract_response_data(response)
    if not data:
        print("No data returned from the server.")
        return
    
    songs = data.get("searchResult2", {}).get("song", [])
    
    for song in songs:
        print(f"{song['title']} - {song['artist']} (ID: {song['id']})")
    
    if not songs:
        print("Nessun risultato trovato.")