import pandas as pd

# Path del dataset consolidato
CONSOLIDATED_PATH = 'data/consolidated-products.csv'

# Caricamento del dataset
def load_and_inspect():
    df = pd.read_csv(CONSOLIDATED_PATH)
    print("Preview of Consolidated Dataset:")
    print(df.head())
    print("\nDataset Info:")
    print(df.info())
    return df

# Esegui le operazioni di validazione
if __name__ == '__main__':
    print("Loading and inspecting the consolidated dataset...")
    df = load_and_inspect()
