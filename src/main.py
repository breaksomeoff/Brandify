from flask import Flask, render_template
from data.data_preprocessing_pipeline import preprocess_data
from src.recommendation.recommendation_engine_tfidf import RecommendationEngineTFIDF
from api.spotify import spotify_bp
from api.recommendations import recommendations_bp
import config

def create_app():
    app = Flask(__name__)
    app.secret_key = config.FLASK_SECRET_KEY

    # Preprocessing Dataset
    print("Caricamento e preprocessing dataset...")
    df_products = preprocess_data(
        csv_path=config.DATASET_PATH,
        bigram_min_freq=config.BIGRAM_MIN_FREQ,
        bigram_pmi_threshold=config.BIGRAM_PMI_THRESHOLD,
        trigram_min_freq=config.TRIGRAM_MIN_FREQ,
        trigram_pmi_threshold=config.TRIGRAM_PMI_THRESHOLD,
    )

    # Inizializzazione RecommendationEngineTFIDF
    print("Inizializzazione RecommendationEngineTFIDF...")
    engine = RecommendationEngineTFIDF()
    engine.fit(df_products, ngram_range=(1, 3))
    app.config["RECOMMENDER_ENGINE_TFIDF"] = engine

    # Registrazione i blueprint
    app.register_blueprint(spotify_bp, url_prefix='/spotify')
    app.register_blueprint(recommendations_bp, url_prefix='/recommendations')

    @app.route('/')
    def home():
        return render_template('home.html')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
