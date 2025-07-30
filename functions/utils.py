import hashlib
import random
import string
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === CONFIG ENV ===
class __Config:
    """Configuration class to hold environment variables."""
    def __init__(self):
        self.server_url = os.getenv("SERVER_URL_NAVIDROME", "")
        self.username = os.getenv("USERNAME_NAVIDROME", "")
        self.password = os.getenv("PASSWORD_NAVIDROME", "")
        self.client_name = "myPythonClient"
        self.api_version = "1.16.1"
        self.format = "json"

    def get_server_url(self):
        if not self.server_url:
            raise ValueError("SERVER_URL_NAVIDROME is not set in the environment variables.")
        return self.server_url

    def get_base_params(self):
        token, salt = generate_token(self.password)
        return {
            "u": self.username,
            "t": token,
            "s": salt,
            "v": self.api_version,
            "c": self.client_name,
            "f": self.format,
        }

__config = __Config()

def set_url(url=""):
    return f"{__config.get_server_url()}{url}"

def set_params(opts=None):
    new_params = __config.get_base_params()
    if opts:
        new_params.update(opts)
    return new_params

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