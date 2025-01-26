import os
import secrets
import logging
from dotenv import load_dotenv

# Configurazione del logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Carica variabili d'ambiente da .env
load_dotenv()

# Configurazioni API Spotify - Serve per l'autenticazione Spotify
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
if SPOTIPY_CLIENT_ID is None :
    logger.warning("SPOTIPY_CLIENT_ID non è stato definito nell'ambiente.")

SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
if SPOTIPY_CLIENT_SECRET is None:
    logger.warning("SPOTIPY_CLIENT_SECRET non è stato definito nell'ambiente.")

# Configurazioni API Last.fm - Serve per creare i dizionari
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
if LASTFM_API_KEY is None:
    logger.warning("LASTFM_API_KEY non è stato definito nell'ambiente.")

LASTFM_SHARED_SECRET = os.getenv("LASTFM_SHARED_SECRET")
if LASTFM_SHARED_SECRET is None:
    logger.warning("LASTFM_SHARED_SECRET non è stato definito nell'ambiente.")



# Percorso data prodotti musicali
DATASET_PATH = "../data/music-products.csv"

# Percorsi per i file dizionario
LASTFM_ARTISTS_FILE = "../data/artists.txt"
LASTFM_GENRES_FILE = "../data/genres.txt"

# Attivazione dell'estrazione di dati da Last.fm per creare i dizionari
CREATE_DICTIONARY = False



# Configurazioni per l'Algoritmo Genetico
GA_NUM_GENERATIONS = 200  # Numero iterazioni dell'algoritmo
GA_NUM_PARENTS_MATING = 25  # Numero di genitori selezionati per la riproduzione
GA_SOL_PER_POP = 70  # Numero di soluzioni nella popolazione
GA_MUTATION_PERCENT_GENES = 3  # Percentuale di geni mutati in una soluzione, 3%
GA_CROSSOVER_PROBABILITY = 70  # Probabilità di crossover tra due genitori, 70%
GA_KEEP_ELITISM = 2  # Numero di individui migliori da mantenere intatti a ogni generazione
GA_STAGNATION_LIMIT = 35  # Numero di iterazioni senza miglioramenti per considerare l'algoritmo in stallo

# Pesi per la funzione di fitness
GA_AFFINITY_WEIGHTS = {
    "artists": 10,
    "genres": 15 # Peso maggiore essendo più specifico (i prodotti di artisti saranno molto più numerosi rispetto ai prodotti di genere)
}
GA_PENALTY_WEIGHT_NON_MATCH = 15  # Penalità per ogni prodotto non corrispondente ai gusti dell'utente (falsi positivi)
GA_PENALTY_MISSING_RELEVANT = 15  # Penalità per ogni prodotto "rilevante" non incluso (falsi negativi)



# Flask session secret key
FLASK_SECRET_KEY = secrets.token_hex(32)



# Attivazione dei dati mock (cambiare config.PROFILE_* in recommendations.py)
USE_MOCK_DATA = True

# Profilo 1 - Metal/Rock
PROFILE_1 = {
    "artists": ['slipknot', 'tool', 'deftones', 'alice_in_chains', 'korn', 'mudvayne', 'radiohead', 'city_morgue', 'the_cure', 'led_zeppelin', 'the_beatles', 'title_fight', 'death', 'opeth', 'mastodon', 'bad_religion', 'nofx', 'cannibal_corpse'],
    "genres": ['metal', 'nu_metal', 'alternative_metal', 'rock', 'hard_rock', 'progressive_metal', 'industrial_metal', 'classic_rock', 'psychedelic_rock', 'rap_metal', 'indie_rock', 'grunge', 'alternative_rock', 'punk_rock'],
    "recent_artists": ['tool', 'slipknot', 'mudvayne', 'korn', 'death', 'city_morgue', 'radiohead', 'alice_in_chains', 'deftones', 'led_zeppelin', 'the_beatles', 'the_cure', 'title_fight', 'black_sabbath', 'nine_inch_nails', 'system_of_a_down', 'rage_against_the_machine'],
    "recent_genres": ['metal', 'nu_metal', 'alternative_metal', 'industrial_metal', 'rap_metal', 'rock', 'hard_rock', 'classic_rock', 'progressive_rock', 'grunge', 'industrial_rock', 'heavy_metal', 'thrash_metal', 'death_metal', 'punk']
}

# Profilo 2 - Hip-Hop/Trap
PROFILE_2 = {
    "artists": ['drake', 'kendrick_lamar', 'travis_scott', 'future', 'playboi_carti', 'lil_uzi_vert', 'lil_baby', 'kanye_west', 'jay_z', 'bad_bunny', 'uicideboy', 'xxxtentacion', 'lil_peep', 'dmx', 'eminem', 'geolier', 'daddy_yankee'],
    "genres": ['hip_hop', 'trap', 'rap', 'underground_hip_hop', 'dark_trap', 'emo_rap', 'cloud_rap', 'horrorcore', 'rap_metal', 'drill', 'melodic_rap'],
    "recent_artists": ['travis_scott', 'drake', 'future', 'lil_baby', 'playboi_carti', 'bad_bunny', 'peso_pluma', 'kendrick_lamar', 'kanye_west', 'lil_uzi_vert', 'uicideboy', 'xxxtentacion', 'city_morgue', 'eminem', 'jay_z'],
    "recent_genres": ['trap', 'hip_hop', 'rap', 'dark_trap', 'melodic_rap', 'emo_rap', 'drill', 'underground_hip_hop', 'horrorcore', 'mumble_rap', 'conscious_rap', 'alternative_rap']
}

# Profilo 3 - Pop/Electronic
PROFILE_3 = {
    "artists": ['taylor_swift', 'ariana_grande', 'the_weeknd', 'billie_eilish', 'drake', 'bad_bunny', 'bjrk', 'the_prodigy', 'gigi_dagostino', 'radiohead', 'pino_daniele', 'bladee', 'lorde'],
    "genres": ['pop', 'electronic', 'dance', 'techno', 'house', 'trance', 'ambient', 'experimental', 'art_pop', 'indie_pop'],
    "recent_artists": ['taylor_swift', 'ariana_grande', 'billie_eilish', 'the_weeknd', 'bjrk', 'the_prodigy', 'bad_bunny', 'drake', 'gigi_dagostino', 'pino_daniele', 'mitski'],
    "recent_genres": ['pop', 'electronic', 'dance', 'techno', 'house', 'trance', 'experimental', 'ambient', 'reggaeton', 'dance_pop', 'art_pop', 'rb']
}



# Attivazione dei test di benchmark
RUN_TESTS = False
