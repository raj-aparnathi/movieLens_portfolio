"""
Build Script: Extract all analysis results from MovieLens 1M .dat files
into lightweight JSON files for the static HTML portfolio.

This script replicates the exact analysis pipeline from DMT.ipynb and
the existing Streamlit data_loader.py, producing JSON output files
that the browser can load directly.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from itertools import combinations
from mlxtend.frequent_patterns import apriori, association_rules
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

DATA_DIR = Path(__file__).parent
OUT_DIR = DATA_DIR / "site" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

AGE_MAP = {
    1: "Under 18", 18: "18-24", 25: "25-34",
    35: "35-44", 45: "45-49", 50: "50-55", 56: "56+"
}

OCCUPATION_MAP = {
    0: "other / not specified", 1: "academic / educator", 2: "artist",
    3: "clerical / admin", 4: "college / grad student", 5: "customer service",
    6: "doctor / health care", 7: "executive / managerial", 8: "farmer",
    9: "homemaker", 10: "K-12 student", 11: "lawyer", 12: "programmer",
    13: "retired", 14: "sales / marketing", 15: "scientist",
    16: "self-employed", 17: "technician / engineer", 18: "tradesman / craftsman",
    19: "unemployed", 20: "writer"
}

AGE_ORDER = ["Under 18", "18-24", "25-34", "35-44", "45-49", "50-55", "56+"]

print("Loading raw data...")
movies = pd.read_csv(DATA_DIR / "movies.dat", sep="::", engine="python",
                     encoding="latin-1", names=["MovieID", "Title", "Genres"])
ratings = pd.read_csv(DATA_DIR / "ratings.dat", sep="::", engine="python",
                      encoding="latin-1", names=["UserID", "MovieID", "Rating", "Timestamp"])
users = pd.read_csv(DATA_DIR / "users.dat", sep="::", engine="python",
                    encoding="latin-1", names=["UserID", "Gender", "Age", "Occupation", "Zip-code"])
users["Age_Group"] = users["Age"].map(AGE_MAP)
users["Occupation_Name"] = users["Occupation"].map(OCCUPATION_MAP)

# ============================================================
# 1. KPI Summary
# ============================================================
print("Computing KPIs...")
distinct_genres = set()
for g in movies["Genres"].str.split("|"):
    distinct_genres.update(g)

rating_counts = ratings["Rating"].value_counts().sort_index()
rating_pcts = (rating_counts / len(ratings) * 100).round(2)

kpis = {
    "total_users": int(len(users)),
    "total_movies": int(len(movies)),
    "total_ratings": int(len(ratings)),
    "distinct_genres_count": len(distinct_genres),
    "genres_list": sorted(list(distinct_genres)),
    "mean_rating": round(float(ratings["Rating"].mean()), 2),
    "min_rating": int(ratings["Rating"].min()),
    "max_rating": int(ratings["Rating"].max()),
    "mode_rating": int(ratings["Rating"].mode()[0]),
    "rating_distribution": {str(k): int(v) for k, v in rating_counts.items()},
    "rating_pcts": {str(k): float(v) for k, v in rating_pcts.items()},
}

with open(OUT_DIR / "kpis.json", "w") as f:
    json.dump(kpis, f)
print("  -> kpis.json")

# ============================================================
# 2. Genre Analytics
# ============================================================
print("Computing genre analytics...")
df = ratings.merge(movies, on="MovieID")
genre_df = df.assign(Genre=df["Genres"].str.split("|")).explode("Genre")

avg_rating = genre_df.groupby("Genre")["Rating"].mean().sort_values(ascending=False)
rating_count = genre_df.groupby("Genre")["Rating"].count().sort_values(ascending=False)

# Compute 5-star percentage per genre using groupby (pandas 3.x compatible)
genre_rating_counts = genre_df.groupby(["Genre", "Rating"]).size().unstack(fill_value=0)
five_star_pct = (genre_rating_counts[5] / genre_rating_counts.sum(axis=1) * 100).sort_values(ascending=False)

genre_analytics = {
    "avg_rating": {k: round(v, 2) for k, v in avg_rating.items()},
    "rating_count": {k: int(v) for k, v in rating_count.items()},
    "five_star_pct": {k: round(v, 2) for k, v in five_star_pct.items()},
}

with open(OUT_DIR / "genre_analytics.json", "w") as f:
    json.dump(genre_analytics, f)
print("  -> genre_analytics.json")

# ============================================================
# 3. Genre Pairs Analysis
# ============================================================
print("Computing genre pairs...")
pair_count = {}
for genres in movies["Genres"]:
    genre_list = genres.split("|")
    for pair in combinations(sorted(genre_list), 2):
        pair_count[pair] = pair_count.get(pair, 0) + 1

top_pairs = sorted(pair_count.items(), key=lambda x: x[1], reverse=True)[:12]

# Rating analysis for pairs
pair_movie_df = movies[["MovieID", "Genres"]].copy()
pair_movie_df["Genre_List"] = pair_movie_df["Genres"].str.split("|")
pair_movie_df = pair_movie_df.explode("Genre_List").rename(columns={"Genre_List": "Genre"})

pair_list = []
for movie_id, group in pair_movie_df.groupby("MovieID"):
    genres = sorted(group["Genre"].unique())
    for pair in combinations(genres, 2):
        pair_list.append({"MovieID": movie_id, "Genre_Pair": f"{pair[0]} + {pair[1]}"})

pair_movie_pairs = pd.DataFrame(pair_list)
pair_rating_analysis = (
    pair_movie_pairs.merge(ratings[["MovieID", "Rating"]], on="MovieID")
    .groupby("Genre_Pair")["Rating"]
    .agg(["count", "mean"])
    .sort_values("count", ascending=False)
)

reliable_pairs = (
    pair_rating_analysis[pair_rating_analysis["count"] >= 500]
    .sort_values("mean", ascending=False)
)

genre_pairs_data = {
    "top_common_pairs": [{"pair": f"{p[0][0]} + {p[0][1]}", "count": int(p[1])} for p in top_pairs],
    "reliable_pairs": [
        {"pair": idx, "count": int(row["count"]), "mean": round(row["mean"], 2)}
        for idx, row in reliable_pairs.head(12).iterrows()
    ],
}

with open(OUT_DIR / "genre_pairs.json", "w") as f:
    json.dump(genre_pairs_data, f)
print("  -> genre_pairs.json")

# ============================================================
# 4. Association Rules (Apriori)
# ============================================================
print("Running Apriori association rules...")
genre_matrix = movies["Genres"].str.get_dummies(sep="|").astype(bool)
frequent_genres = apriori(genre_matrix, min_support=0.02, use_colnames=True)
rules = association_rules(frequent_genres, metric="confidence", min_threshold=0.3)
rules = rules.sort_values("lift", ascending=False).reset_index(drop=True)
rules["Antecedents_Str"] = rules["antecedents"].apply(lambda x: ", ".join(list(x)))
rules["Consequents_Str"] = rules["consequents"].apply(lambda x: ", ".join(list(x)))
rules["Rule"] = rules["Antecedents_Str"] + " → " + rules["Consequents_Str"]

rules_data = {
    "num_frequent_itemsets": int(len(frequent_genres)),
    "num_rules": int(len(rules)),
    "max_lift": round(float(rules["lift"].max()), 2),
    "max_confidence": round(float(rules["confidence"].max()) * 100, 1),
    "top_rule": rules.iloc[0]["Rule"] if not rules.empty else "N/A",
    "rules": [
        {
            "antecedents": row["Antecedents_Str"],
            "consequents": row["Consequents_Str"],
            "rule": row["Rule"],
            "support": round(float(row["support"]) * 100, 2),
            "confidence": round(float(row["confidence"]) * 100, 2),
            "lift": round(float(row["lift"]), 2),
        }
        for _, row in rules.iterrows()
    ],
}

with open(OUT_DIR / "association_rules.json", "w") as f:
    json.dump(rules_data, f)
print("  -> association_rules.json")

# ============================================================
# 5. PCA Analysis
# ============================================================
print("Running PCA analysis...")
genre_df_pca = df.assign(Genre=df["Genres"].str.split("|")).explode("Genre")
user_genre = (
    genre_df_pca.merge(users[["UserID", "Age_Group"]], on="UserID")
    .groupby(["UserID", "Genre"])["Rating"]
    .mean()
    .unstack(fill_value=0)
)

user_age = users.set_index("UserID")["Age_Group"]
user_genre["Age_Group"] = user_genre.index.map(user_age)

X = user_genre.drop(columns=["Age_Group"])
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_scaled)

pca_df = pd.DataFrame(X_pca, columns=["PC1", "PC2"], index=user_genre.index)
pca_df["Age_Group"] = user_genre["Age_Group"].values

loadings = pd.DataFrame(pca.components_.T, columns=["PC1", "PC2"], index=X.columns)

# Sample PCA data for scatter plot (all 6040 users but rounded for smaller JSON)
pca_points = []
for _, row in pca_df.iterrows():
    pca_points.append({
        "pc1": round(float(row["PC1"]), 3),
        "pc2": round(float(row["PC2"]), 3),
        "age": row["Age_Group"]
    })

pca_data = {
    "num_users": int(len(pca_df)),
    "pc1_variance": round(float(pca.explained_variance_ratio_[0]) * 100, 1),
    "pc2_variance": round(float(pca.explained_variance_ratio_[1]) * 100, 1),
    "total_variance": round(float(sum(pca.explained_variance_ratio_)) * 100, 1),
    "loadings": {
        genre: {"pc1": round(float(row["PC1"]), 4), "pc2": round(float(row["PC2"]), 4)}
        for genre, row in loadings.iterrows()
    },
    "points": pca_points,
}

with open(OUT_DIR / "pca.json", "w") as f:
    json.dump(pca_data, f)
print("  -> pca.json")

# ============================================================
# 6. Age-Genre Analysis
# ============================================================
print("Computing age-genre analysis...")
genre_df_age = genre_df.merge(users[["UserID", "Age_Group"]], on="UserID")

genre_age_rating = (
    genre_df_age.groupby(["Age_Group", "Genre"])["Rating"]
    .mean()
    .unstack()
    .reindex(AGE_ORDER)
)

age_genre_count = (
    genre_df_age.groupby(["Age_Group", "Genre"]).size()
    .reset_index(name="Movie_Count")
)

age_ratings = ratings.merge(users[["UserID", "Age_Group"]], on="UserID")
age_avg_rating = age_ratings.groupby("Age_Group")["Rating"].mean().reindex(AGE_ORDER)

# Heatmap data
heatmap_data = {}
for age_group in AGE_ORDER:
    heatmap_data[age_group] = {
        genre: round(float(genre_age_rating.loc[age_group, genre]), 2)
        for genre in sorted(genre_age_rating.columns)
    }

# Top genres per age group
top3_by_age = {}
top5_by_age = {}
for age_group in AGE_ORDER:
    subset = age_genre_count[age_genre_count["Age_Group"] == age_group].sort_values("Movie_Count", ascending=False)
    top3_by_age[age_group] = [
        {"genre": row["Genre"], "count": int(row["Movie_Count"])}
        for _, row in subset.head(3).iterrows()
    ]
    top5_by_age[age_group] = [
        {"genre": row["Genre"], "count": int(row["Movie_Count"])}
        for _, row in subset.head(5).iterrows()
    ]

# Highest rated genre per age bracket
max_genres = []
for age_group in AGE_ORDER:
    row = genre_age_rating.loc[age_group]
    max_genres.append({
        "age_group": age_group,
        "genre": row.idxmax(),
        "rating": round(float(row.max()), 2)
    })

age_genre_data = {
    "heatmap": heatmap_data,
    "genres": sorted(genre_age_rating.columns.tolist()),
    "age_avg_rating": {k: round(float(v), 2) for k, v in age_avg_rating.items()},
    "top3_by_age": top3_by_age,
    "top5_by_age": top5_by_age,
    "max_genres": max_genres,
}

with open(OUT_DIR / "age_genre.json", "w") as f:
    json.dump(age_genre_data, f)
print("  -> age_genre.json")

# ============================================================
# 7. Dataset Samples
# ============================================================
print("Generating dataset samples...")
dataset_samples = {
    "movies_sample": movies.head(15).to_dict(orient="records"),
    "ratings_sample": ratings.head(15).to_dict(orient="records"),
    "users_sample": users[["UserID", "Gender", "Age", "Age_Group", "Occupation", "Occupation_Name", "Zip-code"]].head(15).to_dict(orient="records"),
    "age_distribution": {k: int(v) for k, v in users["Age_Group"].value_counts().reindex(AGE_ORDER).items()},
    "gender_distribution": {k: int(v) for k, v in users["Gender"].value_counts().items()},
    "gender_pcts": {
        "M": round(float(users["Gender"].value_counts(normalize=True)["M"]) * 100, 1),
        "F": round(float(users["Gender"].value_counts(normalize=True)["F"]) * 100, 1),
    },
}

with open(OUT_DIR / "dataset_samples.json", "w") as f:
    json.dump(dataset_samples, f)
print("  -> dataset_samples.json")

# Bundle into data.js for zero-server / offline file:// support
combined = {}
for json_file in OUT_DIR.glob("*.json"):
    with open(json_file, "r", encoding="utf-8") as f:
        combined[json_file.stem] = json.load(f)

with open(OUT_DIR / "data.js", "w", encoding="utf-8") as f:
    f.write("window.DMT_DATA = " + json.dumps(combined) + ";\n")
print("  -> data.js (standalone offline bundle)")

print("\n[SUCCESS] All data files generated in:", OUT_DIR)
print("Total JSON files:", len(list(OUT_DIR.glob("*.json"))))
