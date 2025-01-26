import numpy as np
import pandas as pd
import pygad
import config
from src.recommendation.evaluate_ga import evaluate_recommendations

class RecommendationEngineGA:
    """
    Algoritmo genetico per raccomandare un sottoinsieme di prodotti in base ai gusti dell'utente.
    Utilizza PyGAD come libreria GA.
    In certe funzioni sono richiesti i seguenti parametri anche se inutilizzati: ga_instance, solution_idx. (compabilità con PyGAD)
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

        :param df_products: DataFrame Pandas con i prodotti (colonna "tags").
        :param user_data: Dizionario con i dati dell'utente da Spotify (top e recent).
        :param min_price: Prezzo minimo impostato dall'utente (opzionale).
        :param max_price: Prezzo massimo impostato dall'utente (opzionale).
        :param preference_mode: Modalità di preferenza ("artist", "genre", "balanced").
        """
        # Clona il DataFrame originale per evitare modifiche in-place
        self.df_products = df_products.copy()
        self.user_data = user_data
        self.min_price = min_price
        self.max_price = max_price
        self.preference_mode = preference_mode

        # DataFrame originale per il benchmark
        self.df_all_products = None

        # Parametri GA importati da config.py
        self.num_generations = config.GA_NUM_GENERATIONS
        self.num_parents_mating = config.GA_NUM_PARENTS_MATING
        self.sol_per_pop = config.GA_SOL_PER_POP
        self.mutation_percent_genes = config.GA_MUTATION_PERCENT_GENES
        self.crossover_probability = config.GA_CROSSOVER_PROBABILITY
        self.stagnation_limit = config.GA_STAGNATION_LIMIT
        self.keep_elitism = config.GA_KEEP_ELITISM

        # Traccia del progresso in ottica "stagnazione"
        self.no_improvement_generations = 0
        self.last_best_fitness = None

        # Traccia le generazioni completate
        self.generations_completed = 0

        # Pesi di affinità e penalità prelevati dalla config
        self.affinity_weights = config.GA_AFFINITY_WEIGHTS
        self.penalty_weight_non_match = config.GA_PENALTY_WEIGHT_NON_MATCH
        self.penalty_missing_relevant = config.GA_PENALTY_MISSING_RELEVANT

        # Memorizza tutti i tag associati ai prodotti
        self.products_tags = self.df_products["tags"].tolist()

        # Inizializza un set vuoto per gli indici "rilevanti" (calcolati in recommend())
        self.relevant_indices = set()

    def _reset_stagnation_params(self):
        """
        Reimposta i contatori di stagnazione prima di un nuovo ciclo GA.
        """
        self.no_improvement_generations = 0
        self.last_best_fitness = None

    def _evaluate_product_score(self, product_idx):
        """
        Calcola il punteggio di affinità di un singolo prodotto
        basandosi sul match con i gusti dell'utente (artist/genre).

        :param product_idx: Indice del prodotto nel DataFrame.
        :return: Valore (float o int) che rappresenta il punteggio di affinità.
        """
        # Ricava i tag del prodotto
        p_tags = set(self.products_tags[product_idx])

        # Unisce i set di top e recent per artisti e generi
        user_artists = set(self.user_data.get("artists", [])) | set(self.user_data.get("recent_artists", []))
        user_genres = set(self.user_data.get("genres", [])) | set(self.user_data.get("recent_genres", []))

        # Calcola l'affinità in base alla modalità di preferenza
        affinity_score = 0
        if self.preference_mode == "artist":
            if p_tags & user_artists:
                affinity_score = self.affinity_weights["artists"]
        elif self.preference_mode == "genre":
            if p_tags & user_genres:
                affinity_score = self.affinity_weights["genres"]
        elif self.preference_mode == "balanced":
            if p_tags & user_artists:
                affinity_score += self.affinity_weights["artists"]
            if p_tags & user_genres:
                affinity_score += self.affinity_weights["genres"]

        return affinity_score

    def _fitness_func(self, ga_instance, solution, solution_idx):
        """
        Calcola il punteggio di fitness di una soluzione (insieme binario di prodotti).
        Tiene conto dell'affinità totale, della copertura e della precisione.

        :param ga_instance: Istanza GA in esecuzione.
        :param solution: Array binario che rappresenta una soluzione (1=prodotto selezionato).
        :param solution_idx: Indice della soluzione nella popolazione.
        :return: Punteggio di fitness complessivo (total_affinity - coverage_penalty - precision_penalty).
        """
        selected_indices = np.where(solution == 1)[0]

        # Calcola il punteggio totale di affinità per i prodotti selezionati
        total_affinity = sum(self._evaluate_product_score(idx) for idx in selected_indices)

        # Calcola la penalità di precisione (prodotti selezionati senza affinità)
        precision_penalty = self.penalty_weight_non_match * sum(
            1 for idx in selected_indices if self._evaluate_product_score(idx) == 0
        )

        # Calcola la penalità di copertura (prodotti rilevanti non inclusi)
        selected_set = set(selected_indices)
        missing_relevant_products = self.relevant_indices - selected_set
        coverage_penalty = self.penalty_missing_relevant * len(missing_relevant_products)

        # Restituisce il punteggio netto finale
        return total_affinity - precision_penalty - coverage_penalty

    def _generate_initial_population(self):
        """
        Genera una popolazione iniziale di soluzioni binarie in modo casuale.
        Restituisce un array numpy (matrice) di shape (sol_per_pop, num_prodotti).
        """
        initial_population = []
        while len(initial_population) < self.sol_per_pop:
            individual = np.random.randint(0, 2, size=len(self.df_products))
            initial_population.append(individual)

        return np.array(initial_population)

    def _crossover_func(self, parents, offspring_size, ga_instance):
        """
        Esegue un crossover uniforme sui geni dei genitori. È prevista una
        probabilità di "saltare" la ricombinazione e copiare direttamente un genitore.

        :param parents: Array dei genitori selezionati.
        :param offspring_size: Shape dell'array di figli da generare.
        :param ga_instance: Istanza GA attuale.
        :return: Array numpy con i nuovi individui generati.
        """
        offspring = np.empty(offspring_size, dtype=int)
        for k in range(offspring_size[0]):
            parent1 = parents[k % parents.shape[0]]
            parent2 = parents[(k + 1) % parents.shape[0]]

            # Esegue crossover bit a bit con maschera casuale
            mask = np.random.rand(*parent1.shape) < 0.5
            offspring[k] = np.where(mask, parent1, parent2)

            # Esegue il "salto" del crossover con prob. 1 - (crossover_probability/100)
            if np.random.rand() > (self.crossover_probability / 100.0):
                offspring[k] = parent1.copy()

        return offspring

    def _mutation_func(self, offspring, ga_instance):
        """
        Esegue la mutazione flip dei geni con una certa probabilità.

        :param offspring: Array contenente i figli generati dal crossover.
        :param ga_instance: Istanza GA attuale.
        :return: Array numpy dei figli dopo la mutazione.
        """
        mutation_indices = np.random.rand(*offspring.shape) < (self.mutation_percent_genes / 100.0)
        offspring[mutation_indices] = 1 - offspring[mutation_indices]
        return offspring

    def _on_generation(self, ga_instance):
        """
        Callback eseguito alla fine di ogni generazione. Mostra il miglior fitness
        e controlla la stagnazione, consentendo un'eventuale uscita anticipata.
        """
        best_solution, best_fitness, _ = ga_instance.best_solution()
        print(f"[INFO] Generazione {ga_instance.generations_completed}: Miglior fitness = {best_fitness}")

        # Salva per il benchmark
        self.generations_completed = ga_instance.generations_completed

        # Verifica se non c'è stato miglioramento rispetto alla generazione precedente
        if self.last_best_fitness is not None and best_fitness <= self.last_best_fitness:
            self.no_improvement_generations += 1
        else:
            self.no_improvement_generations = 0
            self.last_best_fitness = best_fitness

        # Effettua lo stop anticipato se si supera la soglia di stagnazione
        if self.no_improvement_generations >= self.stagnation_limit:
            print(f"[INFO] Arresto anticipato: Nessun miglioramento per {self.stagnation_limit} generazioni consecutive.")
            return "stop"

    def recommend(self):
        """
        Avvia il processo GA e restituisce un DataFrame con i prodotti selezionati (geni=1).
        Stampa a schermo le metriche di precisione e copertura finali.
        """
        if self.df_products.empty:
            print("[WARNING] Nessun prodotto disponibile nel DataFrame.")
            return pd.DataFrame()

        # Reimposta i parametri di stagnazione per un nuovo run
        self._reset_stagnation_params()

        # Crea una copia del DataFrame originale per il benchmark
        self.df_all_products = self.df_products.copy()

        # Filtra i prodotti fuori dal range di prezzo prima del processo GA
        if self.min_price is not None:
            self.df_products = self.df_products[self.df_products['price'] >= self.min_price]
        if self.max_price is not None:
            self.df_products = self.df_products[self.df_products['price'] <= self.max_price]

        if self.df_products.empty:
            print("[WARNING] Nessun prodotto disponibile dopo il filtro sul prezzo.")
            return pd.DataFrame()

        # Aggiorna products_tags dopo il filtraggio
        if self.min_price is not None or self.max_price is not None:
            self.df_products['tags'] = self.df_products['tags'].apply(lambda x: x.split(',') if isinstance(x, str) else x)
            self.products_tags = self.df_products["tags"].tolist()

        # Identifica gli indici "rilevanti" da coprire in base alla modalità di preferenza
        print("[INFO] Calcola gli indici dei prodotti rilevanti ai gusti dell'utente...")
        user_artists = set(self.user_data.get("artists", [])) | set(self.user_data.get("recent_artists", []))
        user_genres  = set(self.user_data.get("genres", []))  | set(self.user_data.get("recent_genres", []))

        self.relevant_indices = set()
        relevant_tags = []  # Lista per memorizzare le tag rilevanti
        for idx, tags in enumerate(self.products_tags):
            p_tags = set(tags)

            if self.preference_mode == "artist":
                if p_tags & user_artists:
                    self.relevant_indices.add(idx)
                    relevant_tags.append(tags)
            elif self.preference_mode == "genre":
                if p_tags & user_genres:
                    self.relevant_indices.add(idx)
                    relevant_tags.append(tags)
            elif self.preference_mode == "balanced":
                if (p_tags & user_artists) or (p_tags & user_genres):
                    self.relevant_indices.add(idx)
                    relevant_tags.append(tags)

        print("[INFO] Le tag rilevanti trovate per l'utente sono:", relevant_tags)


        # Crea la popolazione iniziale
        initial_population = self._generate_initial_population()

        # Imposta e avvia l'algoritmo genetico
        ga_instance = pygad.GA(
            num_generations       = self.num_generations,
            num_parents_mating    = self.num_parents_mating,
            fitness_func          = self._fitness_func,
            initial_population    = initial_population,
            crossover_type        = self._crossover_func,
            mutation_type         = self._mutation_func,
            on_generation         = self._on_generation,
            gene_type             = int,
            parent_selection_type = "sss",  # steady state selection
            keep_elitism          = self.keep_elitism
        )

        print("[INFO] Avvio dell'algoritmo genetico...")
        ga_instance.run()
        print("[INFO] GA terminato.")

        # Recupera la miglior soluzione e la fitness associata
        all_fitness = ga_instance.last_generation_fitness
        best_index = np.argmax(all_fitness)
        best_solution = ga_instance.population[best_index]
        best_fitness = all_fitness[best_index]

        print(f"[INFO] Miglior fitness ottenuta: {best_fitness}")

        # Costruisce il DataFrame dei prodotti selezionati
        selected_indices = np.where(best_solution == 1)[0]
        recommended_df = self.df_products.iloc[selected_indices].copy()

        # Mostra i prodotti raccomandati
        if not recommended_df.empty:
            print("[INFO] Prodotti suggeriti:")
            for _, row in recommended_df.iterrows():
                print(f" - {row['name']} ({row['price']} €)\n   Tags: {row['tags']}")
        else:
            print("[INFO] Nessun prodotto selezionato dal GA.")

        # Valuta la precisione e la copertura finale
        precision_cov_metrics = evaluate_recommendations(
            recommended_products=recommended_df,
            df_all_products=self.df_all_products,
            user_data=self.user_data,
            min_price=self.min_price,
            max_price=self.max_price,
            preference_mode=self.preference_mode
        )

        precision_value = precision_cov_metrics["precision"]
        coverage_value = precision_cov_metrics["coverage"]
        missing_relevant = precision_cov_metrics["missing_relevant"]
        missing_relevant_out_of_price = precision_cov_metrics["missing_relevant_out_of_price"]
        artist_mismatched = precision_cov_metrics["artist_mismatched"]
        genre_mismatched = precision_cov_metrics["genre_mismatched"]

        print(f"[INFO] Precisione: {precision_value:.2f}%")
        print(f"[INFO] Copertura: {coverage_value:.2f}%")

        # Elenca i prodotti mancanti se la copertura non è completa
        if coverage_value < 100.0:
            in_range_set = set(missing_relevant) - set(missing_relevant_out_of_price)
            if in_range_set:
                print("\n[INFO] Prodotti pertinenti ai gusti dell'utente ma non raccomandati:")
                for prod in in_range_set:
                    print("  -", prod)

        # Elenca i prodotti mancanti fuori prezzo
        if missing_relevant_out_of_price:
            print("\n[INFO] [RANGE PRICE MODE] Prodotti pertinenti ai gusti dell'utente ma non raccomandati perché fuori prezzo:")
            for prod in missing_relevant_out_of_price:
                print("  -", prod)

        # Elenca prodotti mancanti in base alla modalità di preferenza
        if self.preference_mode == "artist" and genre_mismatched:
            print(
                "\n[INFO] [ARTIST MODE] Prodotti pertinenti ai gusti dell'utente ma non raccomandati perché di genere:")
            for prod in genre_mismatched:
                print("  -", prod)

        if self.preference_mode == "genre" and artist_mismatched:
            print(
                "\n[INFO] [GENRE MODE] Prodotti pertinenti ai gusti dell'utente ma non raccomandati perché di artisti:")
            for prod in artist_mismatched:
                print("  -", prod)

        return recommended_df