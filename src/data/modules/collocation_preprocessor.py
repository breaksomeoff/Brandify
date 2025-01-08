import re
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
from typing import List

class CollocationPreprocessor:
    def __init__(self, bigram_min_freq: int, bigram_pmi_threshold: float,
                 trigram_min_freq: int, trigram_pmi_threshold: float):
        """
        Inizializza il preprocessore con i parametri per bigrammi e trigrammi.

        :param bigram_min_freq: Frequenza minima per i bigrammi.
        :param bigram_pmi_threshold: Soglia PMI per i bigrammi.
        :param trigram_min_freq: Frequenza minima per i trigrammi.
        :param trigram_pmi_threshold: Soglia PMI per i trigrammi.
        """
        self.bigram_min_freq = bigram_min_freq
        self.bigram_pmi_threshold = bigram_pmi_threshold
        self.trigram_min_freq = trigram_min_freq
        self.trigram_pmi_threshold = trigram_pmi_threshold
        self.collocations = []

    def fit(self, texts: List[str]):
        """
        Identifica bigrammi e trigrammi significativi basati su frequenza e PMI.

        :param texts: Lista di testi da analizzare.
        """
        print("Identificazione di bigrammi e trigrammi significativi...")
        all_tokens = [token for text in texts for token in text.split()]

        # Identificazione dei bigrammi
        bigram_finder = BigramCollocationFinder.from_words(all_tokens)
        bigram_finder.apply_freq_filter(self.bigram_min_freq)
        bigram_scored = bigram_finder.score_ngrams(BigramAssocMeasures().pmi)
        for bigram, score in bigram_scored:
            if score >= self.bigram_pmi_threshold:
                self.collocations.append(" ".join(bigram))

        # Identificazione dei trigrammi
        trigram_finder = TrigramCollocationFinder.from_words(all_tokens)
        trigram_finder.apply_freq_filter(self.trigram_min_freq)
        trigram_scored = trigram_finder.score_ngrams(TrigramAssocMeasures().pmi)
        for trigram, score in trigram_scored:
            if score >= self.trigram_pmi_threshold:
                self.collocations.append(" ".join(trigram))

        print(f"Numero totale di collocazioni trovate: {len(self.collocations)}")
        print(f"Esempi di collocazioni: {self.collocations[:10]}")

    def transform_text(self, text: str) -> str:
        """
        Trasforma un singolo testo sostituendo le collocazioni identificate con underscore.

        :param text: Testo da trasformare.
        :return: Testo trasformato.
        """
        for phrase in self.collocations:
            phrase_underscore = phrase.replace(" ", "_")
            pattern = rf"\b{re.escape(phrase)}\b"
            text = re.sub(pattern, phrase_underscore, text)
        return text

    def transform(self, texts: List[str]) -> List[str]:
        """
        Trasforma una lista di testi sostituendo le collocazioni identificate con underscore.

        :param texts: Lista di testi da trasformare.
        :return: Lista di testi trasformati.
        """
        return [self.transform_text(text) for text in texts]
