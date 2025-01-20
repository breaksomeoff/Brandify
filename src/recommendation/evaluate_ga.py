def calculate_match_score(recommended_products, user_data):
    """
    Calcola il punteggio di match tra i prodotti raccomandati e le preferenze dell'utente.

    :param recommended_products: DataFrame con i prodotti raccomandati dal GA (colonne: 'tags').
    :param user_data: Dizionario con i dati dell'utente da Spotify.
    :return: Numero di prodotti con match e numero totale di prodotti raccomandati.
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

        # Calcola i match tra i tag del prodotto e le preferenze dell'utente
        match_genres = product_tags & all_genres
        match_artists = product_tags & all_artists

        if match_genres or match_artists:
            total_matches += 1

    return total_matches, total_products

def calculate_precision(total_matches, total_products):
    """
    Calcola la precisione delle raccomandazioni come percentuale di match.

    :param total_matches: Numero di prodotti che matchano con le preferenze utente.
    :param total_products: Numero totale di prodotti raccomandati.
    :return: Precisione in percentuale (float).
    """
    if total_products == 0:
        return 0.0  # Evita divisioni per zero

    precision = (total_matches / total_products) * 100
    return precision

def evaluate_recommendations(recommended_products, user_data):
    """
    Valuta la precisione delle raccomandazioni restituite dal GA.

    :param recommended_products: DataFrame con i prodotti raccomandati dal GA (colonne: 'tags').
    :param user_data: Dizionario con i dati dell'utente da Spotify.
    :return: Precisione delle raccomandazioni in percentuale.
    """
    total_matches, total_products = calculate_match_score(recommended_products, user_data)
    precision = calculate_precision(total_matches, total_products)

    return precision
