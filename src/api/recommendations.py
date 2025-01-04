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
    min_price = request.form.get('min_price')
    max_price = request.form.get('max_price')
    top_n = request.form.get('top_n')

    # Converti i parametri
    min_price = float(min_price) if min_price and float(min_price) >= 0 else None
    max_price = float(max_price) if max_price and float(max_price) >= 0 else None
    top_n = int(top_n) if top_n and int(top_n) > 0 else None

    token = request.form.get('authorization_token')

    # Recupera i dati da Spotify
    spotify_data = get_spotify_data(token)
    user_artists = spotify_data['artists']
    user_genres = spotify_data['genres']
    recent_artists = spotify_data['recent_artists']
    recent_genres = spotify_data['recent_genres']

    # Stampa i dati recuperati
    print(f"User Artists: {user_artists}")
    print(f"User Genres: {user_genres}")
    print(f"Recent Artists: {recent_artists}")
    print(f"Recent Genres: {recent_genres}")

    # Passa i dati al motore di raccomandazione
    results = engine.recommend(
        user_artists=user_artists,
        user_genres=user_genres,
        spotify_data={
            'recent_artists': recent_artists,
            'recent_genres': recent_genres,
        },
        min_price=min_price,
        max_price=max_price,
        top_n=top_n
    )
    print(results.to_dict(orient='records'))
    return render_template('results.html', results=results.to_dict(orient='records'))
