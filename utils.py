import hashlib
import random
import string


def generate_token(password):
    salt = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    token = hashlib.md5((password + salt).encode()).hexdigest()
    return token, salt


def extract_response_data(response):
    if response.status_code != 200:
        print("Errore nella richiesta:", response.status_code)
        return None

    data = response.json()
    if data.get("subsonic-response", {}).get("error", None):
        print("Errore nella risposta del server:", data["subsonic-response"]["error"]["message"])
        return None

    return data.get("subsonic-response", {})