import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Path del dataset consolidato
CONSOLIDATED_PATH = '../data/consolidated-products.csv'

class RecommendationEngine:
    def __init__(self):
        print("Loading dataset...")
        self.df = pd.read_csv(CONSOLIDATED_PATH)
        print(f"Dataset loaded: {len(self.df)} products")

    def recommend(self, keywords, min_price=None, max_price=None, preferred_brand=None, top_n=5):
        # Filtro per prezzo
        df_filtered = self.df.copy()
        if min_price is not None:
            df_filtered = df_filtered[df_filtered['price'] >= min_price]
        if max_price is not None:
            df_filtered = df_filtered[df_filtered['price'] <= max_price]

        # Filtro per brand
        if preferred_brand:
            df_filtered = df_filtered[df_filtered['brand'].str.contains(preferred_brand, case=False, na=False)]

        # TF-IDF e similarità
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(df_filtered['description'].fillna(''))
        user_query_vector = vectorizer.transform([keywords])

        similarity_scores = cosine_similarity(user_query_vector, tfidf_matrix).flatten()
        df_filtered['similarity'] = similarity_scores

        # Ordina e restituisce i top N prodotti
        recommendations = df_filtered.sort_values(by='similarity', ascending=False).head(top_n)
        return recommendations[['name', 'description', 'price', 'brand', 'image']]
