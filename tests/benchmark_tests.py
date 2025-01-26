import pandas as pd
import matplotlib.pyplot as plt
from src.recommendation.recommendation_engine_ga import RecommendationEngineGA
from src.recommendation.evaluate_ga import evaluate_recommendations
import config
import time
import os

def run_benchmark_tests(df_products):
    # Profili utente
    profiles = {
        "Metal/Rock": config.PROFILE_1,
        "Hip-Hop/Trap": config.PROFILE_2,
        "Pop/Electronic": config.PROFILE_3,
    }

    # Range di prezzo e modalità di ricerca
    price_ranges = [(22, 37), (12, 51), (None, None)]
    search_modes = ["artist", "genre", "balanced"]

    results = []  # Risultati finali

    for profile_name, user_data in profiles.items():
        for min_price, max_price in price_ranges:
            for mode in search_modes:
                print(f"\nEseguendo test: Profilo={profile_name}, Range=({min_price}, {max_price}), Modalità={mode}")

                # Inizializza il motore di raccomandazione
                engine = RecommendationEngineGA(
                    df_products=df_products,
                    user_data=user_data,
                    min_price=min_price,
                    max_price=max_price,
                    preference_mode=mode,
                )

                # Misura il tempo di esecuzione
                start_time = time.time()
                recommended_products = engine.recommend()
                duration = time.time() - start_time

                # Valutazione con evaluate_ga
                metrics = evaluate_recommendations(
                    recommended_products=recommended_products,
                    df_all_products=df_products,  # Usare tutti i prodotti originali
                    user_data=user_data,
                    min_price=min_price,
                    max_price=max_price,
                    preference_mode=mode,
                )

                # Salva i risultati
                results.append({
                    "Profile": profile_name,
                    "Price Range": f"({min_price}, {max_price})",
                    "Mode": mode,
                    "Precision": metrics["precision"],
                    "Coverage": metrics["coverage"],
                    "Missing Relevant": len(metrics["missing_relevant"]),
                    "Missing Relevant bcs Out of Price": len(metrics["missing_relevant_out_of_price"]),
                    "Genre Mismatched": len(metrics["genre_mismatched"]),
                    "Artist Mismatched": len(metrics["artist_mismatched"]),
                    "Best Fitness": engine.last_best_fitness,
                    "Generations": engine.generations_completed,
                    "Duration (s)": duration,
                })

    # Creazione del DataFrame e salvataggio in CSV
    results_df = pd.DataFrame(results)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(base_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    results_csv_path = os.path.join(results_dir, "test_results.csv")
    results_df.to_csv(results_csv_path, index=False)

    # Genera grafici di Precisione e Copertura per ciascun profilo
    for i, profile in enumerate(["Metal/Rock", "Hip-Hop/Trap", "Pop/Electronic"], start=1):
        profile_df = results_df[results_df["Profile"] == profile]

        plt.figure(figsize=(12, 6))
        x = range(len(profile_df))  # Indici x
        bar_width = 0.4

        precision_values = profile_df["Precision"].tolist()
        coverage_values = profile_df["Coverage"].tolist()

        # Precisione
        bars_precision = plt.bar(
            [pos - bar_width / 2 for pos in x],
            precision_values,
            bar_width,
            label="Precisione",
            color="blue"
        )

        # Copertura
        bars_coverage = plt.bar(
            [pos + bar_width / 2 for pos in x],
            coverage_values,
            bar_width,
            label="Copertura",
            color="orange"
        )

        # Etichette asse X
        x_labels = [
            f"{mode}\n{price}"
            for mode, price in zip(profile_df["Mode"], profile_df["Price Range"])
        ]
        plt.xticks(x, x_labels, rotation=45, ha="right")

        plt.title(f"Precisione e Copertura - Profilo {i}: {profile}")
        plt.xlabel("Modalità di Ricerca e Range di Prezzo")
        plt.ylabel("Percentuale (%)")
        plt.legend()
        plt.tight_layout()

        plt.savefig(os.path.join(results_dir, f"Profile{i}_precision_coverage.png"))

    # Genera grafici riguardo le prestazioni del GA per ciascun profilo
    for i, profile in enumerate(["Metal/Rock", "Hip-Hop/Trap", "Pop/Electronic"], start=1):
        profile_df = results_df[results_df["Profile"] == profile]

        plt.figure(figsize=(12, 6))
        x = range(len(profile_df))  # Indici x
        bar_width = 0.3

        fitness_values = profile_df["Best Fitness"].tolist()
        generation_values = profile_df["Generations"].tolist()
        duration_values = profile_df["Duration (s)"].tolist()

        # Fitness
        bars_fitness = plt.bar(
            [pos - bar_width for pos in x],
            fitness_values,
            bar_width,
            label="Max Fitness",
            color="blue"
        )

        # Generazioni
        bars_generations = plt.bar(
            x,
            generation_values,
            bar_width,
            label="Generazioni",
            color="orange"
        )

        # Durata
        bars_duration = plt.bar(
            [pos + bar_width for pos in x],
            duration_values,
            bar_width,
            label="Durata (s)",
            color="green"
        )

        # Aggiunge valori sopra le barre
        for bar, value in zip(bars_fitness, fitness_values):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{value:.0f}",
                ha="center",
                va="bottom"
            )

        for bar, value in zip(bars_generations, generation_values):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{value:.0f}",
                ha="center",
                va="bottom"
            )

        for bar, value in zip(bars_duration, duration_values):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                f"{value:.2f}s",
                ha="center",
                va="bottom"
            )

        # Etichette asse X
        x_labels = [
            f"{mode}\n{price}"
            for mode, price in zip(profile_df["Mode"], profile_df["Price Range"])
        ]
        plt.xticks(x, x_labels, rotation=45, ha="right")

        plt.title(f"Andamento GA - Profilo {i}: {profile}")
        plt.xlabel("Modalità di Ricerca e Range di Prezzo")
        plt.ylabel("Valori")
        plt.legend()
        plt.tight_layout()

        plt.savefig(os.path.join(results_dir, f"Profile{i}_ga_performance.png"))

    print(f"Test completati. Grafici e risultati in CSV generati e salvati correttamente in {results_dir}.")
