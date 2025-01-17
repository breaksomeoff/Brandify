import pprint

from flask import Blueprint, request, jsonify, render_template, session, current_app
from src.api.spotify import get_spotify_data
import config

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/configure', methods=['GET'])
def configure_search():
    token = session.get('authorization_token')
    if not token:
        return jsonify({"error": "Authorization token missing"}), 401
    return render_template('configure_search.html', authorization_token=token)

@recommendations_bp.route('/', methods=['POST'])
def recommendations_results():
    min_price = request.form.get('min_price')
    max_price = request.form.get('max_price')
    preference_mode = request.form.get('preference_mode')
    min_price = float(min_price) if min_price and float(min_price) >= 0 else None
    max_price = float(max_price) if max_price and float(max_price) >= 0 else None

    token = request.form.get('authorization_token')

    if config.USE_MOCK_DATA:
        spotify_data = config.PROFILE_1  # Cambia il profilo secondo la necessità
    else:
        spotify_data = get_spotify_data(token)

    engine = current_app.config["RECOMMENDER_ENGINE_GA"]
    engine.min_price = min_price
    engine.max_price = max_price
    engine.preference_mode = preference_mode
    engine.user_data = spotify_data

    # Dati utente per la visualizzazione in front-end
    user_data = {
        "top_artists": spotify_data.get('user_top_artists', []),
        "top_genres": spotify_data.get('user_top_genres', []),
        "recent_artists": spotify_data.get('user_recent_artists', []),
        "recent_genres": spotify_data.get('user_recent_genres', [])
    }
    print("[DEBUG] User Data:")
    pprint.pprint(user_data)

    df_results = engine.recommend()

    if df_results.empty:
        return render_template('results.html', results=[], user_data=user_data)
    return render_template('results.html', results=df_results.to_dict(orient='records'), user_data=user_data)
