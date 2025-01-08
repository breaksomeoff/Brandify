import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RecommendationEngineTFIDF:
    def __init__(self):
        self.df = None
        self.vectorizer = None
        self.product_tfidf = None

    def fit(self, df_products: pd.DataFrame, ngram_range):
        print("Inizializzazione TF-IDF Vectorizer...")
        self.df = df_products.copy()
        self.df['tfidf_text'] = self.df['name_clean'] + " " + self.df['description_clean']

        self.vectorizer = TfidfVectorizer(ngram_range=ngram_range)
        self.product_tfidf = self.vectorizer.fit_transform(self.df['tfidf_text'].tolist())
        print(f"TF-IDF Matrix shape: {self.product_tfidf.shape}\n")

    def recommend(self, spotify_data: dict, min_price=None, max_price=None, do_rerank=True):
        print("Generazione delle raccomandazioni...")

        user_text = self._build_user_query(spotify_data)
        print(f"User Query: {user_text}\n")

        user_vector = self.vectorizer.transform([user_text])
        print(f"User Vector: {user_vector}\n")

        df_filtered = self.df.copy()
        if min_price is not None:
            df_filtered = df_filtered[df_filtered['price'] >= min_price]
        if max_price is not None:
            df_filtered = df_filtered[df_filtered['price'] <= max_price]
        print(f"Prodotti dopo filtro prezzo: {len(df_filtered)}")

        if df_filtered.empty:
            print("Nessun prodotto soddisfa i criteri di prezzo.")
            return pd.DataFrame()

        subset_tfidf = self.product_tfidf[df_filtered.index, :]
        sim_scores = cosine_similarity(user_vector, subset_tfidf).flatten()
        df_filtered['similarity'] = sim_scores

        df_filtered = df_filtered.sort_values('similarity', ascending=False)
        print("Prodotti ordinati per similarità.\n")

        df_filtered = self._filter_irrelevant(df_filtered, spotify_data)
        print(f"Prodotti rimasti dopo filtraggio: {len(df_filtered)}\n")

        if do_rerank and not df_filtered.empty:
            df_filtered = self._rerank_same_artist(df_filtered, spotify_data)
        print("Re-ranking applicato.\n")

        top15 = df_filtered[['name', 'description', 'price', 'image_url', 'product_url', 'similarity']].head(15)
        print("Top 15 Raccomandazioni:")
        print(top15, "\n")

        return df_filtered[['name', 'description', 'price', 'image_url', 'product_url', 'similarity']]

    def _build_user_query(self, spotify_data: dict) -> str:
        top_artists = set(spotify_data.get('artists', []))
        top_genres = set(spotify_data.get('genres', []))
        rec_artists = set(spotify_data.get('recent_artists', []))
        rec_genres = set(spotify_data.get('recent_genres', []))

        inter_artists = top_artists.intersection(rec_artists)
        inter_genres = top_genres.intersection(rec_genres)

        tokens = []

        for item in inter_artists.union(inter_genres):
            tokens += [item] * 4

        only_top = (top_artists.union(top_genres)) - (inter_artists.union(inter_genres))
        for item in only_top:
            tokens += [item] * 2

        only_recent = (rec_artists.union(rec_genres)) - (inter_artists.union(inter_genres))
        for item in only_recent:
            tokens += [item]

        user_text = " ".join(tokens)
        return user_text.strip()

    def _filter_irrelevant(self, df_sub: pd.DataFrame, spotify_data: dict) -> pd.DataFrame:
        user_artists = set(
            a.lower() for a in (spotify_data.get('artists', []) + spotify_data.get('recent_artists', [])))
        user_genres = set(g.lower() for g in (spotify_data.get('genres', []) + spotify_data.get('recent_genres', [])))

        print("Filtraggio dei prodotti non pertinenti...")
        print(f"User Artists: {user_artists}")
        print(f"User Genres: {user_genres}\n")

        def is_relevant(text: str) -> bool:
            tokens = set(text.split())
            print(f"Verifica prodotto: '{text}'")
            print(f"Token prodotto: {tokens}")
            matching_tokens = tokens.intersection(user_artists.union(user_genres))
            print(f"Token corrispondenti: {matching_tokens}\n")
            return bool(matching_tokens)

        mask = df_sub['tfidf_text'].apply(is_relevant)
        df_ok = df_sub[mask].copy()
        return df_ok

    def _rerank_same_artist(self, df: pd.DataFrame, spotify_data: dict) -> pd.DataFrame:
        user_artists = set(
            a.lower() for a in (spotify_data.get('artists', []) + spotify_data.get('recent_artists', [])))

        def boost_similarity(row):
            tokens = set(row['tfidf_text'].split())
            if user_artists.intersection(tokens):
                return row['similarity'] + 0.02
            return row['similarity']

        similarity_boost = df.apply(boost_similarity, axis=1)
        if len(similarity_boost) != len(df):
            raise ValueError("boost_similarity returned a Series of different length")

        df['similarity'] = similarity_boost
        df = df.sort_values('similarity', ascending=False)
        return df
