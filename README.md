# Brandify

Brandify è un sistema di raccomandazione musicale basato su Flask e sull'API di Spotify. Il progetto nasce come parte del corso universitario Fondamenti di Intelligenza Artificiale, con l'obiettivo di dimostrare l'applicazione di algoritmi genetici per fornire raccomandazioni personalizzate di prodotti musicali in base ai gusti degli utenti.

## Obiettivi del Progetto

1. Dimostrare l'utilizzo di algoritmi genetici in un contesto accademico.
2. Offrire raccomandazioni personalizzate basate sui gusti musicali estratti dai dati di Spotify.
3. Creare un sistema modulare e facilmente estendibile per future sperimentazioni.

## Funzionalità Principali

- Raccomandazioni personalizzate basate sui generi e artisti preferiti degli utenti.
- Integrazione con l'API di Spotify per l'accesso ai dati musicali.
- Utilizzo dell'API di Last.fm per arricchire i dati su artisti e generi musicali.
- Sistema di selezione ottimale dei prodotti musicali tramite algoritmi genetici.
- Interfaccia web per l'interazione con l'utente.

## Struttura del Progetto

```
Brandify/
├── data/                        # Dataset dei prodotti e dizionari utili per il pre-processing
├── src/                         # Codice sorgente
│   ├── api/                     # Moduli API per raccomandazioni e integrazione Spotify
│   ├── preprocessing/           # Script per preprocessare dati e dataset
│   ├── recommendation/          # Algoritmo genetico per raccomandazioni + script di valutazione
│   ├── static/                  # File statici (CSS, immagini prodotti)
│   ├── templates/               # Template HTML per le pagine dell'applicazione
│   └── main.py                  # Punto di ingresso
├── tests/                       # Script di test e benchmarking
├── config.py                    # Configurazione del progetto
├── requirements.txt             # Librerie necessarie
└── .gitignore                   # File di esclusione per Git              
```

## Come Iniziare

Segui questi passaggi per configurare l'ambiente e avviare l'applicazione:

1. **Clona il repository:**

   ```bash
   git clone https://github.com/breaksomeoff/Brandify.git
   cd Brandify
   ```

2. **Crea e attiva l'ambiente virtuale:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Su macOS/Linux
   .venv\Scripts\activate     # Su Windows
   ```

3. **Installa le dipendenze:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configura le variabili d'ambiente:** Crea un file `.env` e aggiungi le seguenti chiavi:

   ```env
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   LASTFM_API_KEY=your_lastfm_api_key
   LASTFM_SHARED_SECRET=your_lastfm_shared_secret
   ```
   oppure utilizza i dati mock definiti nel file `config.py` impostando `USE_MOCK_DATA = True`.


5. **Avvia l'applicazione:**

   ```bash
   python src/main.py
   ```

## Principali Tecnologie Utilizzate

- **Flask:** Framework per lo sviluppo web.
- **Spotify API:** Per accedere ai dati musicali degli utenti.
- **Last.fm API:** Per arricchire i dati su artisti e generi musicali.
- **Algoritmi Genetici:** Per ottimizzare la selezione dei prodotti.
- **Python:** Linguaggio principale del progetto.

## Licenza

Questo progetto è distribuito sotto la licenza MIT. Per maggiori dettagli, consulta il file `LICENSE`.


---

Grazie per aver esplorato Brandify! 🎶

