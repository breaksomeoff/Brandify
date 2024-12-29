from flask import Blueprint, request, jsonify, render_template
from src.recommendation.recommendation_engine import RecommendationEngine
from src.api.spotify import get_spotify_data

# Configurazione Blueprint
recommendations_bp = Blueprint('recommendations', __name__)
engine = RecommendationEngine()

@recommendations_bp.route('/', methods=['GET'])
def recommendations_form():
    # Recupera il token dall'intestazione
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization token missing"}), 401
    return render_template('recommendations_form.html', authorization_token=token)

@recommendations_bp.route('/', methods=['POST'])
def recommendations_results():
    # Recupera il token dal form
    token = request.form.get('authorization_token')
    if not token:
        return jsonify({"error": "Authorization token missing"}), 401

    # Recupera input utente
    min_price = float(request.form.get('min_price', 0))
    max_price = float(request.form.get('max_price', 1000))
    preferred_brand = request.form.get('preferred_brand', None)

    # Recupera dati Spotify
    spotify_data = get_spotify_data(token)
    if not spotify_data['genres'] and not spotify_data['artists']:
        return jsonify({"error": "No relevant data found from Spotify"}), 400

    keywords = " ".join(spotify_data['genres'] + spotify_data['artists'])

    # Genera raccomandazioni
    results = engine.recommend(keywords, min_price, max_price, preferred_brand)
    return render_template('recommendations_results.html', results=results.to_dict(orient='records'), authorization_token=token)
