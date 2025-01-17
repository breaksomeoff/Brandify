from flask import Flask, render_template

# Blueprint Flask
from src.api.spotify import spotify_bp
from src.api.recommendations import recommendations_bp

# GA
from src.recommendation.recommendation_engine_ga import RecommendationEngineGA

# Configurazioni
import config

# Preprocessing per i prodotti
from src.preprocessing.product_preprocessor import preprocess_products

# Last.fm extraction (per generare artists.csv/genres.csv)
from src.preprocessing.lastfm_extraction import save_lastfm_data

def create_app():
    """
    Crea l'app Flask e configura tutti i componenti (GA, blueprint, ecc.).
    """
    app = Flask(__name__)
    app.secret_key = config.FLASK_SECRET_KEY

    # Preprocessing Dataset dei prodotti
    print("[INFO] Caricamento e preprocessing dataset...")
    df_products = preprocess_products(config.DATASET_PATH)
    app.config["DF_PRODUCTS"] = df_products

    # Inizializzazione RecommendationEngineGA
    print("[INFO] Inizializzazione RecommendationEngineGA...")
    engine = RecommendationEngineGA(
        df_products=df_products,
        user_data={},  # Sarà popolato dinamicamente in recommendations.py
        min_price=None, # Sarà popolato dinamicamente in recommendations.py
        max_price=None, # Sarà popolato dinamicamente in recommendations.py
        preference_mode=None # Sarà popolato dinamicamente in recommendations.py
    )
    app.config["RECOMMENDER_ENGINE_GA"] = engine

    # Registrazione blueprint
    app.register_blueprint(spotify_bp, url_prefix='/spotify')
    app.register_blueprint(recommendations_bp, url_prefix='/recommendations')

    @app.route('/')
    def home():
        """Route principale dell'app."""
        return render_template('home.html')

    return app

def create_dictionary():
    print("[INFO] Creazione dei dizionari...")
    save_lastfm_data(genre_limit=100, limit_per_genre=100)
    print("[INFO] Dizionari creati con successo.")

if __name__ == "__main__":
    if config.CREATE_DICTIONARY:
        create_dictionary()
    else:
        app = create_app()
        app.run(debug=True, port=5000)
