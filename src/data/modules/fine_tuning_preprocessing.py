import pandas as pd
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

# Scarica risorse NLTK necessarie
nltk.download('punkt')
nltk.download('stopwords')

# Stopwords combinate (base + specifiche del dominio)
base_stopwords = set(stopwords.words('english'))
products_stopwords = {
    'tshirt', 'tote', 'bag', 'hoodie', 'mug', 'beanie',
    'comfortable', 't-shirt', 'poster', 'keychain', 'vinyl'
}
all_stopwords = base_stopwords.union(products_stopwords)

def clean_text(text: str) -> str:
    """
    Pulisce un testo rimuovendo punteggiatura, stopwords e normalizzando in minuscolo.

    :param text: Stringa da pulire.
    :return: Testo pulito come stringa.
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Rimuove punteggiatura
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in all_stopwords]
    return " ".join(tokens)
