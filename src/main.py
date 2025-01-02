from flask import Flask, render_template
from src.api.spotify import spotify_bp
from src.api.recommendations import recommendations_bp
from dotenv import load_dotenv
import os

# Carica le variabili d'ambiente dal file .env
load_dotenv()

app = Flask(__name__)

# Imposta la secret key dal file .env
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

# Registrazione Blueprint per Spotify
app.register_blueprint(spotify_bp, url_prefix='/spotify')

# Registrazione Blueprint per Recommendations
app.register_blueprint(recommendations_bp, url_prefix='/recommendations')

# Route base per verificare il funzionamento del server
@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
