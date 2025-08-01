import csv
import os
import requests
from functions.utils import *

ARTISTS_CACHE_FILE = "./cache/navidrome_artists.csv"
SONGS_CACHE_FILE = "./cache/navidrome_songs.csv"

def get_artists(force_refresh=False):
    if not force_refresh and os.path.exists(ARTISTS_CACHE_FILE):
        try:
            with open(ARTISTS_CACHE_FILE, "r", encoding="utf-8", newline='') as f:
                reader = csv.DictReader(f)
                artist_list = list(reader)
            print(f"Cache found: {len(artist_list)} artists read from '{ARTISTS_CACHE_FILE}'")
            return artist_list
        except Exception as e:
            print(f"Error reading artist cache: {e}")

    print("Downloading all artists from Navidrome server...")

    request = requests.get(set_url("/rest/getArtists.view"), params=set_params())
    request.raise_for_status()
    artists_data = request.json()["subsonic-response"]["artists"]
    artist_list = []

    for group in artists_data.get("index", []):
        artist_list.extend(group.get("artist", []))

    # Only keep Name and Id
    filtered_artists = [{"id": a["id"], "name": a["name"]} for a in artist_list if "id" in a and "name" in a]

    try:
        os.makedirs(os.path.dirname(ARTISTS_CACHE_FILE), exist_ok=True)
        with open(ARTISTS_CACHE_FILE, "w", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["id", "name"])
            writer.writeheader()
            writer.writerows(filtered_artists)
        print(f"Cache updated with {len(filtered_artists)} artists in '{ARTISTS_CACHE_FILE}'")
    except Exception as e:
        print(f"Error saving artist cache: {e}")

    return filtered_artists

def get_albums_by_artist(artist_id):
    params = set_params({
        "id": artist_id
    })
    r = requests.get(set_url("/rest/getArtist.view"), params=params)
    r.raise_for_status()
    return r.json()["subsonic-response"]["artist"].get("album", [])

def get_songs_by_album(album_id):
    params = set_params({
        "id": album_id
    })
    r = requests.get(set_url("/rest/getAlbum.view"), params=params)
    r.raise_for_status()
    return r.json()["subsonic-response"]["album"].get("song", [])

def fetch_all_songs(force_refresh=False):
    if not force_refresh and os.path.exists(SONGS_CACHE_FILE):
        try:
            cached_songs = []
            with open(SONGS_CACHE_FILE, "r", encoding="utf-8", newline='') as f:
                reader = csv.DictReader(f)
                cached_songs = list(reader)
            print(f"📁 Cache trovata: {len(cached_songs)} brani letti da '{SONGS_CACHE_FILE}'")
            return cached_songs
        except Exception as e:
            print(f"Error reading cache: {e}")

    print("Downloading all songs from Navidrome server...")

    artist_list = get_artists(force_refresh=force_refresh)
    all_songs = []

    progress_artist = 0
    total_artists = len(artist_list)

    for artist in artist_list:
        progress_artist += 1
        print(f"Processing artist {progress_artist * 100 // total_artists}%")
        albums = get_albums_by_artist(artist["id"])
        if not albums:
            print(f"No albums found for artist: {artist['name']}")
            continue
        else:
            for album in albums:
                songs = get_songs_by_album(album["id"])
                if not songs:
                    print(f"No songs found for album: {album['name']} by {artist['name']}")
                    continue
                else:
                    all_songs.extend(songs)

    print(f"Completed: {len(all_songs)} brani trovati.")
    
    if not all_songs:
        print("No songs found in the library.")
        return []

    try:
        os.makedirs(os.path.dirname(SONGS_CACHE_FILE), exist_ok=True)
        
        filtered_songs = [
            {"id": s["id"], "title": s["title"], "artist": s["artist"], "artist_id": s["artistId"], "album": s["album"], "album_id": s["albumId"]}
            for s in all_songs if "id" in s and "title" in s
        ]

        all_keys = set()
        for song in filtered_songs:
            all_keys.update(song.keys())
        
        fieldnames = sorted(list(all_keys))
        
        with open(SONGS_CACHE_FILE, "w", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered_songs)

        print(f"Cache updated with {len(filtered_songs)} songs in '{SONGS_CACHE_FILE}'")
    except Exception as e:
        print(f"Error saving cache: {e}")

    return filtered_songs

def search_songs_from_cache(song_artist_list=[]):
    if not os.path.exists(SONGS_CACHE_FILE):
        print(f"Cache file '{SONGS_CACHE_FILE}' does not exist. Please fetch songs first.")
        return []
    try:
        with open(SONGS_CACHE_FILE, "r", encoding="utf-8", newline='') as f:
            reader = csv.DictReader(f)
            cached_songs = list(reader)
    except Exception as e:
        print(f"Error reading cache: {e}")
        return []

    matched_songs = []
    not_found_songs = []

    for song in song_artist_list:
        title = song.get("title", "")
        artist = song.get("artist", "")
        matches = [
            song for song in cached_songs
            if title.lower() in song.get('title', '').lower()
            and artist.lower() in song.get('artist', '').lower()
        ]
        if matches:
            print(f"✅ Found {len(matches)} matches for '{title}' by '{artist}'")
            matched_songs.extend(matches)
        else:
            print(f"❌ No matches found for '{title}' by '{artist}'")
            not_found_songs.append(song)

    return matched_songs, not_found_songs
