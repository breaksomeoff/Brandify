from flask import Blueprint, request, jsonify, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Configurazione Blueprint
spotify_bp = Blueprint('spotify', __name__)

# Configurazione Spotipy
SPOTIPY_CLIENT_ID = '36066d0ce6994f35a1207641ed6cbb9c'
SPOTIPY_CLIENT_SECRET = '07932028d64248d8a75fc22f015535b6'
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/spotify/callback'
SCOPE = 'user-library-read playlist-read-private user-top-read'

sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE
)


# Rotte per l'autenticazione
@spotify_bp.route('/login', methods=['GET'])
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@spotify_bp.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    return jsonify({"access_token": token_info['access_token']})


# Rotte per il recupero dei dati
@spotify_bp.route('/playlists', methods=['GET'])
def get_playlists():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization token missing"}), 401

    sp = spotipy.Spotify(auth=token)
    playlists = sp.current_user_playlists()

    response = []
    for playlist in playlists['items']:
        response.append({
            'name': playlist['name'],
            'tracks_url': playlist['tracks']['href']
        })

    return jsonify(response)


@spotify_bp.route('/top-tracks', methods=['GET'])
def get_top_tracks():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization token missing"}), 401

    sp = spotipy.Spotify(auth=token)
    top_tracks = sp.current_user_top_tracks()

    response = []
    for track in top_tracks['items']:
        response.append({
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name']
        })

    return jsonify(response)