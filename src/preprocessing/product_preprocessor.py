import pandas as pd
import os
import re
import config

########################################
# STOPWORDS & NOISE
########################################
# Rimuove termini irrilevanti per il matching
# (Non rimuoviamo alcune troppo generiche essendo che potrebbero essere incluse in nomi di artisti)
STOPWORDS = {
    "fans", "fan",
    "hits", "hit",
    "feat", "an", "for",
    "featuring", "inspired", "celebrating", "collection",
    "classic", "curated", "top", "exclusive", "iconic", "timeless",
    "vibrant", "unique", "rugged", "stylish", "comfortable", "premium",
    "best", "perfect", "scene", "high-energy", "designed", "music",
    "culture", "artwork", "album", "bands", "style", "movement",
    "t-shirt", "hoodie", "mug", "cap", "poster", "vinyl", "beanie", "keychain",
    "bag", "tote bag", "rumours"
}


########################################
# DIZIONARY LOADER
########################################
def load_dictionary(dict_path):
    """
    Carica un file di testo (es. artists.csv, genres.csv) e restituisce
    un set di stringhe in minuscolo (una per riga).
    Presuppone che i file siano già minuscolizzati in lastfm_extraction.py.
    """
    if not os.path.exists(dict_path):
        print(f"[WARNING] Dizionario non trovato in: {dict_path}")
        return set()

    with open(dict_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    # Già minuscolizzato, quindi facciamo solo .lower() se necessario
    return set(line.lower() for line in lines)


########################################
# SUBSTRING MATCHING
########################################
def dictionary_lookup(text, dictionary_items):
    """
    Cerca i termini di 'dictionary_items' (in minuscolo) all'interno
    di 'text' (anch'esso in minuscolo).
    - Ritorna un set di match trovati, trasformando " " in "_"
      (es. "black metal" -> "black_metal").
    - Ordina per numero di parole e lunghezza (descending), così "black metal"
      precede "metal".
    - Una volta trovato un termine, "consuma" il testo sostituendolo con spazi,
      per evitare di matchare anche il termine più corto.
    """
    matched = set()

    # Ordina i termini dal più "lungo" (in termini di parole e caratteri) al più corto
    sorted_items = sorted(
        dictionary_items,
        key=lambda x: (len(x.split()), len(x)),
        reverse=True
    )

    # Consuma il testo
    temp_text = text
    for item in sorted_items:
        if item in temp_text:
            matched.add(item.replace(" ", "_"))
            replace_str = " " * len(item)  # stessa lunghezza di item
            temp_text = temp_text.replace(item, replace_str, 1)

    return matched

########################################
# PULIZIA TAG
########################################
def clean_special_characters(tags):
    """
    Rimuove caratteri speciali da ciascun tag nella lista.
    """
    cleaned_tags = [re.sub(r'[^a-zA-Z0-9_]', '', tag) for tag in tags]
    return cleaned_tags

########################################
# PREPROCESS CORE
########################################
def preprocess_products(csv_path):
    """
    1) Carica il CSV dei prodotti (music-products.csv).
    2) Carica i dizionari di ARTISTI e GENERI (da config.LASTFM_ARTISTS_FILE, LASTFM_GENRES_FILE).
    3) Per ogni riga:
       - Combina name + description
       - Rimuove alcune stopwords
       - Converte in minuscolo
       - Effettua substring matching (dictionary_lookup)
         dando priorità ai sub-generi (black_metal) su generi più brevi (metal)
       - Rimuove eventuali tag “sottoinsieme” (es. se "black_metal" è trovato,
         rimuove "black" e "metal" dalla tag, serve a distinguere correttamente i sub-generi dai generi durante la raccomandazione).
       - Rimuove caratteri speciali dai tag.
    4) Salva i risultati in df["tags"] e restituisce il DataFrame.
    """
    print("[INFO] Inizio preprocessing dei prodotti.")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"[ERRORE] File dei prodotti non trovato in: {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"[INFO] {len(df)} prodotti caricati da {csv_path}.")

    # Carica i dizionari di artisti e generi
    artists_set = load_dictionary(config.LASTFM_ARTISTS_FILE)
    genres_set = load_dictionary(config.LASTFM_GENRES_FILE)

    def clean_and_lookup(name, description):
        # Combina name e description
        text = f"{name} {description}"

        # Rimuove STOPWORDS.
        tokens = text.split()
        cleaned_tokens = [t for t in tokens if t.lower() not in STOPWORDS]
        cleaned_text = " ".join(cleaned_tokens).lower()

        # Dizionario: cerca artisti
        found_artists = dictionary_lookup(cleaned_text, artists_set)
        # Dizionario: cerca generi
        found_genres = dictionary_lookup(cleaned_text, genres_set)

        # Rimuove caratteri speciali dai risultati del dizionario
        found_artists = list(clean_special_characters(found_artists))
        found_genres = list(clean_special_characters(found_genres))

        # Unione
        tags = list(set(found_artists).union(set(found_genres)))

        # Rimuovi tag sottoinsieme:
        # es. se "black_metal" e "metal" coesistono, tieni solo "black_metal"
        # ad es. "indie_rock" e "rock" coesistono -> tieni "indie_rock"
        filtered_tags = []
        for tag in tags:
            # se non è vero che "tag" è sottoinsieme di "other_tag"
            # es. "tag in other_tag" => scartiamo tag
            if not any(tag in other_tag and tag != other_tag for other_tag in tags):
                filtered_tags.append(tag)

        return filtered_tags

    def extract_tags_for_row(row):
        return clean_and_lookup(row["name"], row["description"])

    df["tags"] = df.apply(extract_tags_for_row, axis=1)

    print("[INFO] Preprocessing completato.")

    # Stampa tutte le tag estratte
    print("\n[DEBUG] Tutte le tag estratte per ciascun prodotto:")
    for i, row in df.iterrows():
        print(f" {row['name']} -> {row['tags']}")

    return df
