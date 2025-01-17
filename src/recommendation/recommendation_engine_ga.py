import numpy as np
import pandas as pd
import pygad
import config
from src.recommendation.evaluate_ga import evaluate_recommendations

class RecommendationEngineGA:
    """
    Algoritmo genetico per raccomandare un sottoinsieme di prodotti in base ai gusti dell'utente.
    Utilizza PyGAD come libreria GA.
    """
    def __init__(
        self,
        df_products,
        user_data,
        min_price=None,
        max_price=None,
        preference_mode=None  # 'artist', 'genre', o 'balanced'
    ):
        """
        Inizializza il motore di raccomandazione GA.

        :param df_products: DataFrame Pandas con i prodotti filtrati, con colonna "tags".
        :param user_data: Dizionario con i dati dell'utente da Spotify (top e recent).
        :param min_price: Prezzo minimo per filtrare i prodotti (facoltativo).
        :param max_price: Prezzo massimo per filtrare i prodotti (facoltativo).
        :param preference_mode: Modalità di preferenza ("artist", "genre", "balanced").
        """
        self.df_products = df_products.copy()
        self.user_data = user_data
        self.min_price = min_price
        self.max_price = max_price
        self.preference_mode = preference_mode

        # Parametri GA da config.py
        self.num_generations = config.GA_NUM_GENERATIONS
        self.num_parents_mating = config.GA_NUM_PARENTS_MATING
        self.sol_per_pop = config.GA_SOL_PER_POP
        self.mutation_percent_genes = config.GA_MUTATION_PERCENT_GENES
        self.crossover_probability = config.GA_CROSSOVER_PROBABILITY
        self.ga_min_products = config.GA_MIN_PRODUCTS

        # Pesi di affinità & penalità
        self.affinity_weights = config.AFFINITY_WEIGHTS
        self.penalty_weight_non_match = config.PENALTY_WEIGHT_NON_MATCH

        # Adatta i pesi in base alla modalità di preferenza
        if preference_mode == "artist":
            # Raddoppia i pesi orientati agli artisti
            self.affinity_weights["shared_artists"] *= 2
            self.affinity_weights["only_top_artists"] *= 2
            self.affinity_weights["only_recent_artists"] *= 2
            # e dimezza quelli dei generi
            self.affinity_weights["shared_genres"] = max(1, self.affinity_weights["shared_genres"] // 2)
            self.affinity_weights["only_top_genres"] = max(1, self.affinity_weights["only_top_genres"] // 2)
            self.affinity_weights["only_recent_genres"] = max(1, self.affinity_weights["only_recent_genres"] // 2)

        elif preference_mode == "genre":
            # Raddoppia i pesi orientati ai generi
            self.affinity_weights["shared_genres"] *= 2
            self.affinity_weights["only_top_genres"] *= 2
            self.affinity_weights["only_recent_genres"] *= 2
            # e dimezza quelli degli artisti
            self.affinity_weights["shared_artists"] = max(1, self.affinity_weights["shared_artists"] // 2)
            self.affinity_weights["only_top_artists"] = max(1, self.affinity_weights["only_top_artists"] // 2)
            self.affinity_weights["only_recent_artists"] = max(1, self.affinity_weights["only_recent_artists"] // 2)

        # Filtra i prodotti in base al prezzo
        self._filter_by_price()

        # Estrai i tag per ciascun prodotto
        self.products_tags = self.df_products["tags"].tolist()

    def _filter_by_price(self):
        """
        Filtra i prodotti in base a min_price e max_price e aggiorna self.df_products.
        """
        if self.min_price is not None:
            self.df_products = self.df_products[self.df_products["price"] >= self.min_price]
        if self.max_price is not None:
            self.df_products = self.df_products[self.df_products["price"] <= self.max_price]
        self.df_products.reset_index(drop=True, inplace=True)

    def _calculate_affinity_and_penalty(self, p_tags):
        """
        Calcola il punteggio di affinità e la penalità per un set di tag di prodotto.

        :param p_tags: Insieme di tag associati a un prodotto.
        :return: (affinity_score, penalty).
        """
        top_genres = set(self.user_data.get("genres", []))
        top_artists = set(self.user_data.get("artists", []))
        recent_genres = set(self.user_data.get("recent_genres", []))
        recent_artists = set(self.user_data.get("recent_artists", []))
        """
        print("\n[DEBUG] Processing Product Tags:", p_tags)
        print("[DEBUG] User Data - Top Artists:", top_artists)
        print("[DEBUG] User Data - Recent Artists:", recent_artists)
        print("[DEBUG] User Data - Top Genres:", top_genres)
        print("[DEBUG] User Data - Recent Genres:", recent_genres)
        """
        # Match tra tag prodotto e preferenze utente
        shared_artists_tags = (p_tags & top_artists) & recent_artists
        shared_genres_tags = (p_tags & top_genres) & recent_genres
        only_top_artists = (p_tags & top_artists) - recent_artists
        only_top_genres = (p_tags & top_genres) - recent_genres
        only_recent_artists = (p_tags & recent_artists) - top_artists
        only_recent_genres = (p_tags & recent_genres) - top_genres
        """
        # Debug sui calcoli degli insiemi
        print("[DEBUG] Shared Artists Tags:", shared_artists_tags)
        print("[DEBUG] Shared Genres Tags:", shared_genres_tags)
        print("[DEBUG] Only Top Artists:", only_top_artists)
        print("[DEBUG] Only Top Genres:", only_top_genres)
        print("[DEBUG] Only Recent Artists:", only_recent_artists)
        print("[DEBUG] Only Recent Genres:", only_recent_genres)
        """
        # Calcolo del punteggio di affinità
        affinity_score = (
                len(shared_genres_tags) * self.affinity_weights["shared_genres"] +
                len(shared_artists_tags) * self.affinity_weights["shared_artists"] +
                len(only_top_genres) * self.affinity_weights["only_top_genres"] +
                len(only_top_artists) * self.affinity_weights["only_top_artists"] +
                len(only_recent_genres) * self.affinity_weights["only_recent_genres"] +
                len(only_recent_artists) * self.affinity_weights["only_recent_artists"]
        )
        """
        # Debug del punteggio di affinità
        print("[DEBUG] Affinity Score Calculation:")
        print("  Shared Genres Score:", len(shared_genres_tags), "*", self.affinity_weights["shared_genres"])
        print("  Shared Artists Score:", len(shared_artists_tags), "*", self.affinity_weights["shared_artists"])
        print("  Only Top Genres Score:", len(only_top_genres), "*", self.affinity_weights["only_top_genres"])
        print("  Only Top Artists Score:", len(only_top_artists), "*", self.affinity_weights["only_top_artists"])
        print("  Only Recent Genres Score:", len(only_recent_genres), "*", self.affinity_weights["only_recent_genres"])
        print("  Only Recent Artists Score:", len(only_recent_artists), "*",
              self.affinity_weights["only_recent_artists"])
        print("[DEBUG] Total Affinity Score:", affinity_score)
        """
        # Penalità = penalty_weight_non_match per ogni prodotto che non matcha nulla
        penalty = 0 if affinity_score > 0 else self.penalty_weight_non_match
        """
        # Debug della penalità
        if penalty > 0:
            print("[DEBUG] Penalty Applied:", penalty)
        else:
            print("[DEBUG] No Penalty Applied.")
        """
        return affinity_score, penalty

    def _fitness_func(self, ga_instance, solution, solution_idx):
        """
        Funzione di fitness per PyGAD (>= 2.20.0).

        :param ga_instance: Istanza GA in esecuzione.
        :param solution: Array binario che rappresenta una soluzione.
        :param solution_idx: Indice della soluzione nella popolazione.
        :return: Punteggio di fitness della soluzione.
        """
        selected_indices = np.where(solution == 1)[0]

        total_affinity = 0
        total_penalty  = 0

        for idx in selected_indices:
            p_tags = set(self.products_tags[idx])
            product_affinity, product_penalty = self._calculate_affinity_and_penalty(p_tags)
            total_affinity += product_affinity
            total_penalty  += product_penalty

        return total_affinity - total_penalty

    def _generate_initial_population(self):
        """
        Genera una popolazione iniziale rispettando il vincolo
        minimo di prodotti selezionati (ga_min_products).
        """
        initial_population = []
        while len(initial_population) < self.sol_per_pop:
            individual = np.random.randint(0, 2, size=len(self.df_products))
            # Aggiungiamo l'individuo solo se rispetta il vincolo
            if np.count_nonzero(individual) >= self.ga_min_products:
                initial_population.append(individual)
        return np.array(initial_population)

    def _crossover_func(self, parents, offspring_size, ga_instance):
        """
        Crossover uniforme con probabilità di 'saltare' la ricombinazione.
        """
        offspring = np.empty(offspring_size, dtype=int)
        for k in range(offspring_size[0]):
            parent1 = parents[k % parents.shape[0]]
            parent2 = parents[(k + 1) % parents.shape[0]]

            # Uniform crossover (gene per gene)
            mask = np.random.rand(*parent1.shape) < 0.5
            offspring[k] = np.where(mask, parent1, parent2)

            # Probabilità di "saltare" crossover
            if np.random.rand() > self.crossover_probability:
                offspring[k] = parent1.copy()

        return offspring

    def _mutation_func(self, offspring, ga_instance):
        """
        Flippa i geni con una certa probabilità.
        """
        mutation_indices = np.random.rand(*offspring.shape) < (self.mutation_percent_genes / 100.0)
        offspring[mutation_indices] = 1 - offspring[mutation_indices]
        return offspring

    def _on_generation(self, ga_instance):
        """
        Stampa log informativi a fine generazione.
        """
        best_solution, best_fitness, _ = ga_instance.best_solution()
        print(f"[INFO] Generazione {ga_instance.generations_completed}: Miglior fitness = {best_fitness}")

    def recommend(self):
        """
        Avvia il GA e restituisce un DataFrame con i prodotti selezionati (geni=1).
        """
        if self.df_products.empty:
            print("[WARNING] Nessun prodotto dopo il filtraggio prezzi.")
            return pd.DataFrame()

        # Popolazione iniziale con il vincolo ga_min_products
        initial_population = self._generate_initial_population()

        ga_instance = pygad.GA(
            num_generations        = self.num_generations,
            num_parents_mating     = self.num_parents_mating,
            fitness_func           = self._fitness_func,
            initial_population     = initial_population,
            crossover_type         = self._crossover_func,
            mutation_type          = self._mutation_func,
            on_generation          = self._on_generation,
            gene_type              = int,
            parent_selection_type  = "sss",
        )

        print("[INFO] Avvio dell'algoritmo genetico...")
        ga_instance.run()
        print("[INFO] GA terminato.")

        best_solution, best_fitness, _ = ga_instance.best_solution()
        print(f"[INFO] Miglior fitness: {best_fitness}")

        selected_indices = np.where(best_solution == 1)[0]
        recommended_df   = self.df_products.iloc[selected_indices].copy()

        # Converti la colonna 'tags' in tuple per evitare errori di hashing con drop_duplicates
        recommended_df["tags"] = recommended_df["tags"].apply(tuple)
        recommended_df.drop_duplicates(inplace=True)

        # Debug: stampa i prodotti scelti
        if not recommended_df.empty:
            print("[INFO] Prodotti suggeriti:")
            for _, row in recommended_df.iterrows():
                print(f" - {row['name']} ({row['price']} €)\n   Tags: {row['tags']}")
        else:
            print("[INFO] Nessun prodotto selezionato dal GA.")

        # Valutazione della precisione
        precision = evaluate_recommendations(recommended_df, self.user_data)
        print(f"[INFO] Precisione finale delle raccomandazioni: {precision:.2f}%")

        return recommended_df
