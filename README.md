# Brandify

Brandify è un sistema di raccomandazione musicale basato su Flask e Spotify API, progettato per suggerire prodotti e gadget musicali in base ai gusti degli utenti.

---

## Funzionalità
- Raccomandazioni personalizzate basate sulle playlist Spotify.
- Interfaccia RESTful per la comunicazione con il backend.
- Sistema modulare per futuri miglioramenti.

## Struttura del Progetto
```plaintext
Brandify/
├── src/                # Codice sorgente
│   ├── main.py         # Punto di ingresso
│   ├── api/            # Moduli API
├── tests/              # Test unitari
├── requirements.txt    # Librerie necessarie
├── .gitignore          # File di esclusione per Git
└── README.md           # Documentazione del progetto
```

## Come Iniziare
1. Clona il repository:
   git clone https://github.com/tuo-username/Brandify.git
   cd Brandify

2. Attiva l'ambiente virtuale:
   Su macOS/Linux:
   source .venv/bin/activate
   Su Windows:
   .venv\Scripts\activate

3. Installa le dipendenze:
   pip install -r requirements.txt

4. Avvia l'app:
   python src/main.py

## Tecnologie Utilizzate
- Flask: Backend API RESTful.
- Spotipy: Integrazione con Spotify API.
- Python: Linguaggio principale.
- Pandas/Numpy: Manipolazione e analisi dati.

---

## Licenza
Questo progetto è distribuito sotto la licenza MIT.
