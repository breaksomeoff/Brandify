from flask import Blueprint, request, jsonify, render_template, session, current_app
from src.api.spotify import get_spotify_data, get_spotify_token
import config

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/configure', methods=['GET'])
def configure_search():
    use_mock = request.args.get('mock', 'false').lower() == 'true'

    if use_mock and config.USE_MOCK_DATA:
        # Usa i dati mock senza controllare il token
        return render_template('configure_search.html', authorization_token="mock-token")

    # Controllo token normale
    token = session.get('authorization_token')
    if not token:
        return jsonify({"error": "Authorization token missing"}), 401

    return render_template('configure_search.html', authorization_token=token)

@recommendations_bp.route('/', methods=['POST'])
def recommendations_results():
    min_price = request.form.get('min_price')
    max_price = request.form.get('max_price')
    preference_mode = request.form.get('preference_mode')
    spotify_token = get_spotify_token()
    min_price = float(min_price) if min_price and float(min_price) >= 0 else None
    max_price = float(max_price) if max_price and float(max_price) >= 0 else None

    if config.USE_MOCK_DATA:
        spotify_data = config.PROFILE_1  # Cambiare il profilo a seconda della necessità (vedi config.py)
        print("[DEBUG] Spotify Mock Data:")
        print(f"Mock Top Artists: {spotify_data['artists']}")
        print(f"Mock Top Genres: {spotify_data['genres']}")
        print(f"Mock Recent Artists: {spotify_data['recent_artists']}")
        print(f"Mock Recent Genres: {spotify_data['recent_genres']}")
    else:
        spotify_data = get_spotify_data(spotify_token)

    engine = current_app.config["RECOMMENDER_ENGINE_GA"]
    engine.min_price = min_price
    engine.max_price = max_price
    engine.preference_mode = preference_mode
    engine.user_data = spotify_data

    df_results = engine.recommend()

    if df_results.empty:
        return render_template('results.html', results=[])
    return render_template('results.html', results=df_results.to_dict(orient='records'))
