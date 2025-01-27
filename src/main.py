from flask import Flask, render_template

# Blueprint Flask
from src.api.spotify import spotify_bp
from src.api.recommendations import recommendations_bp

# Configurazioni
import config

# Preprocessing per i prodotti
from src.preprocessing.product_preprocessor import preprocess_products

# GA
from src.recommendation.recommendation_engine_ga import RecommendationEngineGA

# Last.fm extraction (per generare artists.txt/genres.txt - dizionari)
from src.preprocessing.lastfm_extraction import save_lastfm_data

# Benchmark tests
from tests.benchmark_tests import run_benchmark_tests

def create_app():
    """
    Crea l'app Flask e configura tutti i componenti (GA, blueprint, ecc.).
    """
    app = Flask(__name__)
    app.secret_key = config.FLASK_SECRET_KEY

    # Preprocessing del data contenente i prodotti
    print("[INFO] Caricamento e preprocessing data...")
    df_products = preprocess_products(config.DATASET_PATH)
    app.config["DF_PRODUCTS"] = df_products

    # Inizializza RecommendationEngineGA
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
        return render_template('home.html', use_mock_data=config.USE_MOCK_DATA)

    return app

def create_dictionary():
    print("[INFO] Creazione dei dizionari...")
    save_lastfm_data(genre_limit=100, limit_per_genre=100)
    print("[INFO] Dizionari creati con successo.")

def tests():
    print("[INFO] Caricamento e preprocessing data per i tests...")
    df_products = preprocess_products(config.DATASET_PATH)
    run_benchmark_tests(df_products)

if __name__ == "__main__":
    if config.CREATE_DICTIONARY:
        create_dictionary()
    elif config.RUN_TESTS:
        tests()
    else:
        app = create_app()
        app.run(debug=True, port=5000)
