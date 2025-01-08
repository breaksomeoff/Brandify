from flask import Blueprint, request, jsonify, render_template, session, current_app
from src.api.spotify import get_spotify_data

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
    min_price = float(min_price) if min_price and float(min_price) >= 0 else None
    max_price = float(max_price) if max_price and float(max_price) >= 0 else None

    token = request.form.get('authorization_token')
    spotify_data = get_spotify_data(token)

    engine = current_app.config["RECOMMENDER_ENGINE_TFIDF"]

    df_results = engine.recommend(
        spotify_data=spotify_data,
        min_price=min_price,
        max_price=max_price,
        do_rerank=True
    )

    if df_results.empty:
        return render_template('results.html', results=[])
    return render_template('results.html', results=df_results.to_dict(orient='records'))
