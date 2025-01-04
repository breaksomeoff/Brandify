from flask import Blueprint, request, redirect, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Configurazione Blueprint
spotify_bp = Blueprint('spotify', __name__)

# Configurazione Spotipy
SPOTIPY_CLIENT_ID = '36066d0ce6994f35a1207641ed6cbb9c'
SPOTIPY_CLIENT_SECRET = '07932028d64248d8a75fc22f015535b6'
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/spotify/callback'
SCOPE = 'user-library-read user-top-read user-read-recently-played'



sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE
)

# Rotta per l'autenticazione
@spotify_bp.route('/login', methods=['GET'])
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# Rotta per il logout
@spotify_bp.route('/logout', methods=['GET'])
def logout():
    import os
    if os.path.exists('.cache'):
        os.remove('.cache')  # Rimuove la cache per forzare un nuovo login
    return redirect('/')

@spotify_bp.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    # Salva il token nella sessione
    session['authorization_token'] = token_info['access_token']

    # Reindirizza alla pagina di configurazione
    return redirect(url_for('recommendations.configure_search'))

# Recupera dati da Spotify
@spotify_bp.route('/data', methods=['GET'])
def get_spotify_data(token):
    sp = spotipy.Spotify(auth=token)

    # Top tracks
    top_tracks = sp.current_user_top_tracks(limit=20)['items']

    # Recent played
    recently_played = sp.current_user_recently_played(limit=20)['items']

    genres = []
    artists = []
    recent_genres = []
    recent_artists = []

    for track in top_tracks:
        for artist in track['artists']:
            artist_data = sp.artist(artist['id'])
            genres.extend(artist_data.get('genres', []))
            artists.append(artist['name'])

    for item in recently_played:
        for artist in item['track']['artists']:
            artist_data = sp.artist(artist['id'])
            recent_genres.extend(artist_data.get('genres', []))
            recent_artists.append(artist['name'])

    return {
        'genres': list(set(genres)),
        'artists': list(set(artists)),
        'recent_genres': list(set(recent_genres)),
        'recent_artists': list(set(recent_artists)),
    }
