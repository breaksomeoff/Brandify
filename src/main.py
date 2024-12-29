from flask import Flask
from src.api.spotify import spotify_bp

app = Flask(__name__)

# Registrazione Blueprint per Spotify
app.register_blueprint(spotify_bp, url_prefix='/spotify')

# Route base per verificare il funzionamento del server
@app.route('/')
def home():
    return "Benvenuto in Brandify! Il server è attivo."

if __name__ == '__main__':
    app.run(debug=True, port=5000)



