from flask import Blueprint, request, jsonify, render_template, session
from src.recommendation.recommendation_engine import RecommendationEngine
from src.api.spotify import get_spotify_data

# Configurazione Blueprint
recommendations_bp = Blueprint('recommendations', __name__)
engine = RecommendationEngine()

@recommendations_bp.route('/configure', methods=['GET'])
def configure_search():
    token = session.get('authorization_token')
    if not token:
        return jsonify({"error": "Authorization token missing"}), 401
    return render_template('configure_search.html', authorization_token=token)

@recommendations_bp.route('/', methods=['POST'])
def recommendations_results():
    # Recupera parametri dal form
    min_price = float(request.form.get('min_price', 0))
    max_price = float(request.form.get('max_price', 1000))
    preferred_brand = request.form.get('preferred_brand', None)
    token = request.form.get('authorization_token')

    spotify_data = get_spotify_data(token)
    keywords = " ".join(spotify_data['genres'] + spotify_data['artists'])

    results = engine.recommend(keywords, min_price, max_price, preferred_brand)
    return render_template('results.html', results=results.to_dict(orient='records'))

