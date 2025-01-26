import requests
import config
import os

# Legge la chiave API di Last.fm da config.py
API_KEY = config.LASTFM_API_KEY
BASE_URL = "https://ws.audioscrobbler.com/2.0/"


def make_request(params):
    """
    Effettua una richiesta GET all'API di Last.fm con i parametri specificati.
    In caso di errore di rete o status code non 200, ritorna un dizionario vuoto.
    """
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[ERRORE] Errore nella richiesta a Last.fm: {e}")
        return {}


def get_genres(limit=100):
    """
    Ottiene una lista di generi da Last.fm (tag globali più popolari).

    :param limit: Numero massimo di generi da recuperare
    :return: Lista di stringhe, ognuna corrispondente a un genere (in minuscolo)
    """
    params = {
        "method": "tag.getTopTags",
        "api_key": API_KEY,
        "format": "json",
        "limit": limit
    }
    data = make_request(params)
    tags = data.get("toptags", {}).get("tag", [])
    # Estrarre i tag dalla struttura di Last.fm e normalizzarli (minuscolo, strip)
    genres = []
    for tag in tags:
        name = tag.get("name")
        if name:
            # Converti in minuscolo
            genres.append(name.strip().lower())
    return genres


def get_artists_by_genre(genre, limit=100):
    """
    Ottiene gli artisti associati a un genere specifico su Last.fm.

    :param genre: Nome del genere (stringa)
    :param limit: Numero massimo di artisti da recuperare
    :return: Lista di nomi di artisti (stringhe, in minuscolo)
    """
    params = {
        "method": "tag.getTopArtists",
        "api_key": API_KEY,
        "format": "json",
        "limit": limit,
        "tag": genre
    }
    data = make_request(params)
    artists = data.get("topartists", {}).get("artist", [])
    artist_list = []
    for art in artists:
        name = art.get("name")
        if name:
            artist_list.append(name.strip().lower())
    return artist_list


def get_all_artists(genre_limit=50, limit_per_genre=50):
    """
    Recupera i generi globali (fino a genre_limit) e, per ognuno,
    scarica fino a limit_per_genre artisti. Restituisce un set di artisti
    complessivo (poi convertito in list) in minuscolo.

    :param genre_limit: Numero massimo di generi da considerare
    :param limit_per_genre: Numero massimo di artisti da recuperare per ogni genere
    :return: Lista unica di nomi di artisti (in minuscolo)
    """
    print(f"[INFO] Recupero i primi {genre_limit} generi globali da Last.fm...")
    genres = get_genres(limit=genre_limit)

    all_artists = set()
    for g in genres:
        print(f"[INFO] → Recupero fino a {limit_per_genre} artisti per il genere: {g}")
        artists = get_artists_by_genre(g, limit=limit_per_genre)
        if artists:
            all_artists.update(artists)

    return list(all_artists)


def save_lastfm_data(genre_limit=100, limit_per_genre=100):
    """
    Scarica i generi e gli artisti da Last.fm e li salva in formato testo,
    uno per riga, nei file definiti in config.py (LASTFM_GENRES_FILE e LASTFM_ARTISTS_FILE).
    I generi e gli artisti vengono convertiti in minuscolo per coerenza
    con il dictionary lookup che si effettua successivamente.

    :param genre_limit: Numero massimo di generi da recuperare
    :param limit_per_genre: Numero massimo di artisti da recuperare per ogni genere
    """
    print("[INFO] Inizio salvataggio dati Last.fm...")

    # 1) Scarica i generi (in minuscolo)
    print(f"[INFO] Scarico fino a {genre_limit} generi...")
    genres = get_genres(limit=genre_limit)

    # 2) Scarica artisti (in minuscolo)
    print(f"[INFO] Scarico artisti basandomi sui generi...")
    all_artists = get_all_artists(genre_limit=genre_limit, limit_per_genre=limit_per_genre)

    # Crea la cartella "data" se non esiste
    dir_dataset = os.path.dirname(config.LASTFM_GENRES_FILE)
    if dir_dataset and not os.path.exists(dir_dataset):
        os.makedirs(dir_dataset)

    # Salvataggio generi
    print(f"[INFO] Salvataggio generi in {config.LASTFM_GENRES_FILE}")
    with open(config.LASTFM_GENRES_FILE, "w", encoding="utf-8") as f:
        for g in genres:
            f.write(g.strip() + "\n")

    # Salvataggio artisti
    print(f"[INFO] Salvataggio artisti in {config.LASTFM_ARTISTS_FILE}")
    with open(config.LASTFM_ARTISTS_FILE, "w", encoding="utf-8") as f:
        for art in all_artists:
            f.write(art.strip() + "\n")

    print("[INFO] Salvataggio completato.")
