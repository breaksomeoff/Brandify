from flask import Blueprint, request, redirect, session, url_for, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import re
import os
import config

spotify_bp = Blueprint('spotify', __name__)

SPOTIPY_CLIENT_ID = config.SPOTIPY_CLIENT_ID
SPOTIPY_CLIENT_SECRET = config.SPOTIPY_CLIENT_SECRET
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/spotify/callback'
SCOPE = 'user-library-read user-top-read user-read-recently-played'

sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE
)

def clean_text(text):
    """
    Rimuove caratteri speciali da una stringa e normalizza il testo.
    """
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    return text.replace(" ", "_").lower()

def get_spotify_token():
    """
    Recupera il token dal file di cache.
    """
    token_info = sp_oauth.get_cached_token()
    if token_info and not sp_oauth.is_token_expired(token_info):
        return token_info['access_token']
    return None

@spotify_bp.route('/login', methods=['GET'])
def login():
    if os.path.exists('.cache'):
        os.remove('.cache')
    auth_url = sp_oauth.get_authorize_url() + "&show_dialog=true"
    return redirect(auth_url)

@spotify_bp.route('/logout', methods=['GET'])
def logout():
    if os.path.exists('.cache'):
        os.remove('.cache')
    session.clear()
    return redirect('/')

@spotify_bp.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['authorization_token'] = token_info['access_token']
    return redirect(url_for('recommendations.configure_search'))

def get_spotify_data(token, top_n_genres=15, top_m_artists=15):
    sp = spotipy.Spotify(auth=token)

    top_artists_data = sp.current_user_top_artists(limit=50, time_range='medium_term')['items']
    top_genres = []
    top_artists = []
    for artist in top_artists_data:
        top_genres.extend([clean_text(genre) for genre in artist.get('genres', [])])
        top_artists.append(clean_text(artist['name']))

    recently_played_data = sp.current_user_recently_played(limit=50)['items']
    recent_genres = []
    recent_artists = []
    for item in recently_played_data:
        artist = item['track']['artists'][0]
        artist_data = sp.artist(artist['id'])
        recent_genres.extend([clean_text(genre) for genre in artist_data.get('genres', [])])
        recent_artists.append(clean_text(artist_data['name']))

    top_genres = pd.Series(top_genres).value_counts().head(top_n_genres).index.tolist()
    top_artists = pd.Series(top_artists).value_counts().head(top_m_artists).index.tolist()
    recent_genres = pd.Series(recent_genres).value_counts().head(top_n_genres).index.tolist()
    recent_artists = pd.Series(recent_artists).value_counts().head(top_m_artists).index.tolist()

    print("[DEBUG] Spotify User Data:")
    print(f"User Top Artists: {top_artists}")
    print(f"User Top Genres: {top_genres}")
    print(f"User Recent Artists: {recent_artists}")
    print(f"User Recent Genres: {recent_genres}")

    return {
        'genres': top_genres,
        'artists': top_artists,
        'recent_genres': recent_genres,
        'recent_artists': recent_artists
    }

@spotify_bp.route('/data', methods=['GET'])
def spotify_data_route():
    token = session.get('authorization_token')
    if not token:
        return jsonify({"error": "Authorization token missing"}), 401
    spotify_data = get_spotify_data(token)
    return jsonify(spotify_data)
