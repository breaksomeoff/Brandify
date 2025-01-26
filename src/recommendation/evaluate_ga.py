def calculate_match_score(recommended_products, user_data):
    """
    Calcola il punteggio di match tra i prodotti raccomandati e le preferenze dell'utente.
    Restituisce (numero_match, numero_totale_prodotti raccomandati).
    """
    total_matches = 0
    total_products = len(recommended_products)

    if total_products == 0:
        return 0, 0  # Nessun prodotto raccomandato

    # Combina le preferenze unendo top e recent
    all_genres = set(user_data.get("genres", [])) | set(user_data.get("recent_genres", []))
    all_artists = set(user_data.get("artists", [])) | set(user_data.get("recent_artists", []))

    for _, row in recommended_products.iterrows():
        product_tags = set(row["tags"])
        match_genres = product_tags & all_genres
        match_artists = product_tags & all_artists

        if match_genres or match_artists:
            total_matches += 1

    return total_matches, total_products

def calculate_precision(total_matches, total_products):
    """
    Calcola la precisione delle raccomandazioni.
    """
    if total_products == 0:
        return 0.0
    precision = (total_matches / total_products) * 100
    return precision

def calculate_coverage(recommended_products, df_all_products, user_data, min_price=None, max_price=None, preference_mode=None):
    """
    Calcola la copertura delle raccomandazioni.
    """
    # Unione di artisti e generi dalle preferenze utente
    all_genres = set(user_data.get("genres", [])) | set(user_data.get("recent_genres", []))
    all_artists = set(user_data.get("artists", [])) | set(user_data.get("recent_artists", []))

    # Prodotti pertinenti ai gusti dell'utente, separati per artisti e generi
    relevant_artists = df_all_products[df_all_products["tags"].apply(lambda tags: bool(set(tags) & all_artists))]
    relevant_genres = df_all_products[df_all_products["tags"].apply(lambda tags: bool(set(tags) & all_genres))]

    # Filtra i prodotti rilevanti in base alla modalità
    if preference_mode == "artist":
        relevant_products = relevant_artists
    elif preference_mode == "genre":
        relevant_products = relevant_genres
    else:
        relevant_products = df_all_products[
            df_all_products["tags"].apply(lambda tags: bool(set(tags) & all_genres or set(tags) & all_artists))
        ]

    # Prodotti rilevanti fuori dal range di prezzo
    missing_relevant_out_of_price = []
    if min_price is not None or max_price is not None:
        for _, row in relevant_products.iterrows():
            if ((min_price is not None and row["price"] < min_price) or
                (max_price is not None and row["price"] > max_price)):
                missing_relevant_out_of_price.append(row["name"])

    # Applica il filtro di prezzo sui prodotti rilevanti
    if min_price is not None:
        relevant_products = relevant_products[relevant_products['price'] >= min_price]
    if max_price is not None:
        relevant_products = relevant_products[relevant_products['price'] <= max_price]

    # Calcolo della copertura come percentuale
    total_relevant = len(relevant_products)

    if total_relevant == 0:
        coverage = 100.0
        return coverage, [], missing_relevant_out_of_price, [], []

    # Prodotti rilevanti raccomandati
    recommended_relevant = recommended_products[recommended_products.index.isin(relevant_products.index)]
    num_recommended_relevant = len(recommended_relevant)
    coverage = (num_recommended_relevant / total_relevant) * 100

    # Identificazione dei prodotti rilevanti mancanti
    missing_indices = set(relevant_products.index) - set(recommended_relevant.index)
    missing_relevant = relevant_products.loc[list(missing_indices), "name"].tolist()

    # Prodotti mancanti per mismatch
    genre_mismatched = []
    artist_mismatched = []
    if preference_mode == "artist":
        genre_mismatched = relevant_genres[~relevant_genres.index.isin(relevant_products.index)]["name"].tolist()
    elif preference_mode == "genre":
        artist_mismatched = relevant_artists[~relevant_artists.index.isin(relevant_products.index)]["name"].tolist()

    return coverage, missing_relevant, missing_relevant_out_of_price, genre_mismatched, artist_mismatched


def evaluate_recommendations(
    recommended_products,
    df_all_products,
    user_data,
    min_price=None,
    max_price=None,
    preference_mode=None
):
    """
    Valuta la precisione e la copertura delle raccomandazioni restituite dal GA.

    :param recommended_products: DataFrame con i prodotti raccomandati (colonne: 'tags').
    :param df_all_products: DataFrame con TUTTI i prodotti (colonne: 'tags').
    :param user_data: Dizionario con i dati dell'utente da Spotify.
    :param min_price: soglia di prezzo minima (opzionale).
    :param max_price: soglia di prezzo massima (opzionale).
    :param preference_mode: Modalità di preferenza ("artist", "genre", "balanced").
    :return: Dizionario con:
        {
          "precision": float,
          "coverage": float,
          "missing_relevant": list,
          "missing_relevant_out_of_price": list,
          "genre_mismatched": list,
          "artist_mismatched": list,
        }
    """
    # Calcolo della precisione
    total_matches, total_products = calculate_match_score(recommended_products, user_data)
    precision = calculate_precision(total_matches, total_products)

    # Calcolo della copertura (considerando il filtro di prezzo)
    coverage, missing_relevant, missing_relevant_out_of_price, genre_mismatched, artist_mismatched = calculate_coverage(

        recommended_products,
        df_all_products,
        user_data,
        min_price=min_price,
        max_price=max_price,
        preference_mode=preference_mode
    )

    return {
        "precision": precision,
        "coverage": coverage,
        "missing_relevant": missing_relevant,
        "missing_relevant_out_of_price": missing_relevant_out_of_price,
        "genre_mismatched": genre_mismatched,
        "artist_mismatched": artist_mismatched,
    }
