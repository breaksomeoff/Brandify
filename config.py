import os
from dotenv import load_dotenv

# Carica variabili d'ambiente da .env
load_dotenv()

# Configurazioni API Spotify
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

# Configurazioni API Last.fm
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_SHARED_SECRET = os.getenv("LASTFM_SHARED_SECRET")

# Percorso dataset prodotti musicali
DATASET_PATH = "../dataset/music-products.csv"

# Percorsi per i file dizionario
LASTFM_ARTISTS_FILE = "../dataset/artists.csv"
LASTFM_GENRES_FILE = "../dataset/genres.csv"

# Attivazione dell'estrazione di dati da Last.fm per creare i dizionari
CREATE_DICTIONARY = False

# Configurazioni per l'Algoritmo Genetico
GA_NUM_GENERATIONS = 50  # Aumentato per consentire più iterazioni e una migliore esplorazione
GA_NUM_PARENTS_MATING = 10  # Manteniamo il numero di genitori per la varietà
GA_SOL_PER_POP = 35  # Incrementato per aumentare la diversità della popolazione
GA_MUTATION_PERCENT_GENES = 10  # Maggiore esplorazione attraverso la mutazione
GA_CROSSOVER_PROBABILITY = 0.7  # Aumentato per favorire la combinazione di soluzioni
GA_MIN_PRODUCTS = 5  # Soglia minima di prodotti in una soluzione valida

# Pesi per la funzione di fitness
AFFINITY_WEIGHTS = {
    "shared_genres": 10,
    "shared_artists": 12,
    "only_top_genres": 6,
    "only_top_artists": 8,
    "only_recent_genres": 3,
    "only_recent_artists": 4
}

PENALTY_WEIGHT_NON_MATCH = 5  # Penalità per ogni prodotto non corrispondente ai gusti dell'utente


# Flask Config
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "default_secret_key")

# Dati mock Spotify per il testing

# Attivazione dei dati mock (cambiare config.PROFILE_* in recommendations.py)
USE_MOCK_DATA = False

# Profilo 1 - Metal/Rock
PROFILE_1 = {
    "artists": ['slipknot', 'tool', 'deftones', 'alice_in_chains', 'korn', 'mudvayne', 'radiohead', 'city_morgue', 'the_cure', 'led_zeppelin', 'the_beatles', 'title_fight'],
    "genres": ['metal', 'nu_metal', 'alternative_metal', 'rock', 'hard_rock', 'progressive_metal', 'industrial_metal', 'classic_rock', 'psychedelic_rock', 'rap_metal', 'indie_rock', 'grunge', 'alternative_rock', 'punk_rock'],
    "recent_artists": ['tool', 'slipknot', 'mudvayne', 'korn', 'city_morgue', 'radiohead', 'alice_in_chains', 'deftones', 'led_zeppelin', 'the_beatles', 'the_cure', 'title_fight', 'black_sabbath', 'nine_inch_nails', 'system_of_a_down'],
    "recent_genres": ['metal', 'nu_metal', 'alternative_metal', 'industrial_metal', 'rap_metal', 'rock', 'hard_rock', 'classic_rock', 'progressive_rock', 'grunge', 'industrial_rock', 'heavy_metal', 'thrash_metal', 'death_metal']
}

# Profilo 2 - Hip-Hop/Trap
PROFILE_2 = {
    "artists": ['drake', 'kendrick_lamar', 'travis_scott', 'future', 'playboi_carti', 'lil_uzi_vert', 'lil_baby', 'kanye_west', 'jay_z', 'bad_bunny', 'uicideboy', 'xxxtentacion', 'lil_peep', 'dmx', 'eminem'],
    "genres": ['hip_hop', 'trap', 'rap', 'underground_hip_hop', 'dark_trap', 'emo_rap', 'cloud_rap', 'horrorcore', 'rap_metal', 'drill', 'melodic_rap'],
    "recent_artists": ['travis_scott', 'drake', 'future', 'lil_baby', 'playboi_carti', 'bad_bunny', 'peso_pluma', 'kendrick_lamar', 'kanye_west', 'lil_uzi_vert', 'uicideboy', 'xxxtentacion', 'city_morgue', 'eminem', 'jay_z'],
    "recent_genres": ['trap', 'hip_hop', 'rap', 'dark_trap', 'melodic_rap', 'emo_rap', 'drill', 'underground_hip_hop', 'horrorcore', 'mumble_rap', 'conscious_rap', 'alternative_rap']
}

# Profilo 3 - Pop/Electronic
PROFILE_3 = {
    "artists": ['taylor_swift', 'ariana_grande', 'the_weeknd', 'billie_eilish', 'drake', 'bad_bunny', 'bjrk', 'the_prodigy', 'gigi_dagostino', 'radiohead', 'peso_pluma', 'pino_daniele', 'geolier', 'bladee'],
    "genres": ['pop', 'electronic', 'dance', 'techno', 'house', 'trance', 'ambient', 'experimental', 'art_pop', 'indie_pop'],
    "recent_artists": ['taylor_swift', 'ariana_grande', 'billie_eilish', 'the_weeknd', 'bjrk', 'the_prodigy', 'bad_bunny', 'peso_pluma', 'drake', 'gigi_dagostino', 'pino_daniele', 'geolier'],
    "recent_genres": ['pop', 'electronic', 'dance', 'techno', 'house', 'trance', 'experimental', 'ambient', 'reggaeton', 'dance_pop', 'art_pop', 'rb']
}

