import pandas as pd
from src.data.modules.fine_tuning_preprocessing import clean_text
from src.data.modules.collocation_preprocessor import CollocationPreprocessor

def preprocess_data(
    csv_path,
    bigram_min_freq,
    bigram_pmi_threshold,
    trigram_min_freq,
    trigram_pmi_threshold
):
    """
    Preprocessa il dataset applicando pulizia e identificazione di collocazioni.

    :param csv_path: Percorso del dataset CSV.
    :return: DataFrame preprocessato.
    """
    print(f"Caricamento del dataset da {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Dataset caricato con {len(df)} righe.\n")

    # Stampa le prime 10 righe del dataset originale
    print("Prime 10 righe del dataset originale:")
    print(df.head(10).to_string(index=False))
    print("\n")

    print("Eseguendo pulizia del testo...")
    df['name_clean'] = df['name'].apply(clean_text)
    df['description_clean'] = df['description'].apply(clean_text)
    print("Pulizia del testo completata.\n")

    print("Identificazione di bigrammi e trigrammi significativi...")
    collocation_processor = CollocationPreprocessor(
        bigram_min_freq=bigram_min_freq,
        bigram_pmi_threshold=bigram_pmi_threshold,
        trigram_min_freq=trigram_min_freq,
        trigram_pmi_threshold=trigram_pmi_threshold,
    )
    # Usa 'name_clean' e 'description_clean' per identificare le collocazioni
    combined_texts = (df['name_clean'] + " " + df['description_clean']).tolist()
    collocation_processor.fit(combined_texts)
    print("Collocazioni trovate:")
    print(collocation_processor.collocations[:10], "...\n")

    print("Applicazione delle collocazioni...")
    df['name_clean'] = collocation_processor.transform(df['name_clean'])
    df['description_clean'] = collocation_processor.transform(df['description_clean'])
    print("Trasformazione completata.\n")

    # Stampa le prime 10 righe del DataFrame preprocessato
    print("Prime 10 righe del dataset post-preprocessing:")
    print(df[['name_clean', 'description_clean', 'price']].head(10).to_string(index=False))
    print("\n")

    print("Preprocessing completato!")
    return df
