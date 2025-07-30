import os
import requests
from dotenv import load_dotenv
from utils import *

# Load environment variables from .env file
load_dotenv('./navidrome/.env')

# === CONFIG ENV ===
SERVER_URL = os.getenv("SERVER_URL_NAVIDROME")
USERNAME = os.getenv("USERNAME_NAVIDROME")
PASSWORD = os.getenv("PASSWORD_NAVIDROME")
CLIENT_NAME = "myPythonClient"
API_VERSION = "1.16.1"
FORMAT = "json"


def ping_server() -> int:
    token, salt = generate_token(PASSWORD)
    params = {
        "u": USERNAME,
        "t": token,
        "s": salt,
        "v": API_VERSION,
        "c": CLIENT_NAME,
        "f": FORMAT,
    }
    url = f"{SERVER_URL}/rest/ping.view"
    response = requests.get(url, params=params)
    data = extract_response_data(response)
    if data:
        print("Server is reachable.")
        return 0
    else:
        print("Failed to reach the server.")
        return -1

def search_music(query, search_type="song", limit=10):
    token, salt = generate_token(PASSWORD)

    params = {
        "u": USERNAME,
        "t": token,
        "s": salt,
        "v": API_VERSION,
        "c": CLIENT_NAME,
        "f": FORMAT,
        "query": query,
        "type": search_type,
        "songCount": limit,
    }

    url = f"{SERVER_URL}/rest/search2.view"
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


def main():
    query = input("Cerca una canzone: ")
    if ping_server() == -1:
        return
    search_music(query)


if __name__ == "__main__":
    main()
