import os
from dotenv import load_dotenv

# Carica variabili d'ambiente dal file .env
load_dotenv()

# Configurazioni API Spotify
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:5000/spotify/callback")

# Percorsi file
DATASET_PATH = "../dataset/music-products.csv"
PROCESSED_DATASET_PATH = "../dataset/processed_music_products.csv"

# Soglie per bigrammi/trigrammi
BIGRAM_MIN_FREQ = 3
BIGRAM_PMI_THRESHOLD = 4.0
TRIGRAM_MIN_FREQ = 2
TRIGRAM_PMI_THRESHOLD = 2.5

# Flask Config
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "default_secret_key")
