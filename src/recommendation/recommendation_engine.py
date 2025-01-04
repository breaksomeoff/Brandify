import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Path del dataset
DATASET_PATH = '../data/music-products.csv'

class RecommendationEngine:
    def __init__(self):
        print("Loading dataset...")
        self.df = pd.read_csv(DATASET_PATH)
        print(f"Dataset loaded: {len(self.df)} products")

    def _apply_attention_weights(self, tfidf_matrix):
        """Applica un meccanismo di Self-Attention per pesare le caratteristiche rilevanti."""
        attention_weights = np.mean(tfidf_matrix.toarray(), axis=0)
        weighted_matrix = tfidf_matrix.multiply(attention_weights)
        return weighted_matrix

    def _filter_by_recency(self, spotify_data):
        """Applica un filtro basato sulla cronologia di ascolto (frequenza e recency)."""
        recency_scores = {}

        for artist in spotify_data.get('recent_artists', []):
            recency_scores[artist] = recency_scores.get(artist, 0) + 1

        for genre in spotify_data.get('recent_genres', []):
            recency_scores[genre] = recency_scores.get(genre, 0) + 1

        return recency_scores

    def _get_dominant_genres(self, user_genres, recent_genres):
        """Restituisce i generi dominanti basandosi sulla frequenza."""
        combined_genres = user_genres + recent_genres
        genre_counts = pd.Series(combined_genres).value_counts()
        dominant_genres = genre_counts[genre_counts > 1].index.tolist()  # Generi che appaiono più di una volta
        return dominant_genres

    def recommend(self, user_artists, user_genres, spotify_data, min_price=None, max_price=None, top_n=None):
        # Filtro per prezzo
        df_filtered = self.df.copy()
        if min_price is not None and min_price >= 0:
            df_filtered = df_filtered[df_filtered['price'] >= min_price]
        if max_price is not None and max_price >= 0:
            df_filtered = df_filtered[df_filtered['price'] <= max_price]

        # Identifica i generi dominanti
        dominant_genres = self._get_dominant_genres(user_genres, spotify_data.get('recent_genres', []))
        print(f"Dominant Genres: {dominant_genres}")

        # Costruzione della query utente
        query = " ".join(user_artists + dominant_genres)

        # TF-IDF e similarità
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(df_filtered['description'].fillna(''))

        # Applica Self-Attention per pesare le caratteristiche
        weighted_tfidf_matrix = self._apply_attention_weights(tfidf_matrix)

        # Vettore della query dell'utente
        user_query_vector = vectorizer.transform([query])

        # Similarità con il meccanismo di Self-Attention
        similarity_scores = cosine_similarity(user_query_vector, weighted_tfidf_matrix).flatten()
        df_filtered['similarity'] = similarity_scores

        # Filtro per generi esatti (priorità ai prodotti che contengono generi dell'utente)
        def contains_exact_genre(description):
            return any(genre.lower() in description.lower() for genre in dominant_genres)

        df_filtered['exact_genre_match'] = df_filtered['description'].apply(contains_exact_genre)

        # Filtro per artisti esatti
        def contains_exact_artist(description):
            return any(artist.lower() in description.lower() for artist in user_artists)

        df_filtered['exact_artist_match'] = df_filtered['description'].apply(contains_exact_artist)

        # Filtraggio basato sulla cronologia
        recency_scores = self._filter_by_recency(spotify_data)

        def calculate_recency_score(row):
            score = 0
            for artist in user_artists:
                if artist in recency_scores:
                    score += recency_scores[artist]
            for genre in dominant_genres:
                if genre in recency_scores:
                    score += recency_scores[genre]
            return score

        df_filtered['recency_score'] = df_filtered.apply(calculate_recency_score, axis=1)

        # Ordina i risultati con priorità a corrispondenze esatte, similarità e recency
        recommendations = df_filtered.sort_values(by=['exact_artist_match', 'exact_genre_match', 'recency_score', 'similarity'], ascending=[False, False, False, False])

        # Se top_n è definito, restituisci solo i primi N risultati
        if top_n:
            recommendations = recommendations.head(top_n)

        return recommendations[['name', 'description', 'price', 'image_url', 'product_url']]
