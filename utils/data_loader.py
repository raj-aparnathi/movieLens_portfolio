import os
from pathlib import Path
from itertools import combinations
import pandas as pd
import numpy as np
import streamlit as st
from mlxtend.frequent_patterns import apriori, association_rules
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import plotly.express as px

# Directory resolution
def get_data_dir() -> Path:
    """Resolve directory containing the MovieLens .dat files."""
    candidates = [
        Path(__file__).parent.parent,
        Path.cwd() / "movieLens_portfolio",
        Path.cwd(),
    ]
    for c in candidates:
        if (c / "movies.dat").exists() and (c / "ratings.dat").exists():
            return c
    return Path.cwd()

DATA_DIR = get_data_dir()

AGE_MAP = {
    1: "Under 18",
    18: "18-24",
    25: "25-34",
    35: "35-44",
    45: "45-49",
    50: "50-55",
    56: "56+"
}

OCCUPATION_MAP = {
    0: "other / not specified",
    1: "academic / educator",
    2: "artist",
    3: "clerical / admin",
    4: "college / grad student",
    5: "customer service",
    6: "doctor / health care",
    7: "executive / managerial",
    8: "farmer",
    9: "homemaker",
    10: "K-12 student",
    11: "lawyer",
    12: "programmer",
    13: "retired",
    14: "sales / marketing",
    15: "scientist",
    16: "self-employed",
    17: "technician / engineer",
    18: "tradesman / craftsman",
    19: "unemployed",
    20: "writer"
}

@st.cache_data(show_spinner=False)
def load_raw_data():
    """Load raw MovieLens 1M datasets with original format and encodings."""
    data_dir = get_data_dir()
    movies_path = data_dir / "movies.dat"
    ratings_path = data_dir / "ratings.dat"
    users_path = data_dir / "users.dat"

    movies = pd.read_csv(
        movies_path,
        sep="::",
        engine="python",
        encoding="latin-1",
        names=["MovieID", "Title", "Genres"]
    )

    ratings = pd.read_csv(
        ratings_path,
        sep="::",
        engine="python",
        encoding="latin-1",
        names=["UserID", "MovieID", "Rating", "Timestamp"]
    )

    users = pd.read_csv(
        users_path,
        sep="::",
        engine="python",
        encoding="latin-1",
        names=["UserID", "Gender", "Age", "Occupation", "Zip-code"]
    )

    users["Age_Group"] = users["Age"].map(AGE_MAP)
    users["Occupation_Name"] = users["Occupation"].map(OCCUPATION_MAP)

    return movies, ratings, users

@st.cache_data(show_spinner=False)
def get_kpi_summary():
    """Extract baseline dataset metrics."""
    movies, ratings, users = load_raw_data()
    distinct_genres = set()
    for g in movies["Genres"].str.split("|"):
        distinct_genres.update(g)
    
    return {
        "total_users": int(len(users)),
        "total_movies": int(len(movies)),
        "total_ratings": int(len(ratings)),
        "distinct_genres_count": len(distinct_genres),
        "genres_list": sorted(list(distinct_genres)),
        "mean_rating": float(ratings["Rating"].mean()),
        "min_rating": int(ratings["Rating"].min()),
        "max_rating": int(ratings["Rating"].max()),
        "mode_rating": int(ratings["Rating"].mode()[0]),
    }

@st.cache_data(show_spinner=False)
def get_genre_df():
    """Compute exploded genre dataframe merged with ratings and users."""
    movies, ratings, users = load_raw_data()
    df = ratings.merge(movies, on="MovieID")
    genre_df = df.assign(Genre=df["Genres"].str.split("|")).explode("Genre")
    return genre_df

@st.cache_data(show_spinner=False)
def get_genre_analytics():
    """Calculate aggregated genre ratings, frequency counts, and 5-star distribution."""
    genre_df = get_genre_df()
    
    avg_rating = genre_df.groupby("Genre")["Rating"].mean().sort_values(ascending=False)
    rating_count = genre_df.groupby("Genre")["Rating"].count().sort_values(ascending=False)
    
    # Rating distribution per genre
    crosstab_dist = pd.crosstab(genre_df["Genre"], genre_df["Rating"])
    five_star_pct = (crosstab_dist[5] / crosstab_dist.sum(axis=1) * 100).sort_values(ascending=False)
    
    genre_summary = pd.DataFrame({
        "Genre": avg_rating.index,
        "Average_Rating": avg_rating.values,
        "Total_Ratings": rating_count.reindex(avg_rating.index).values,
        "Five_Star_Pct": five_star_pct.reindex(avg_rating.index).values
    })
    
    return {
        "avg_rating": avg_rating,
        "rating_count": rating_count,
        "crosstab_dist": crosstab_dist,
        "five_star_pct": five_star_pct,
        "genre_summary": genre_summary
    }

@st.cache_data(show_spinner=False)
def get_genre_pairs_analysis():
    """Compute co-occurring genre pairs count and ratings from DMT.ipynb."""
    movies, ratings, _ = load_raw_data()
    
    # Movie level pair counts
    pair_count = {}
    for genres in movies["Genres"]:
        genre_list = genres.split("|")
        for pair in combinations(sorted(genre_list), 2):
            pair_count[pair] = pair_count.get(pair, 0) + 1
            
    genre_pairs_count = (
        pd.Series(pair_count, name="Movie_Count")
        .sort_values(ascending=False)
    )
    
    # Explode genre pairs per movie to calculate rating performance
    pair_movie_df = movies[["MovieID", "Genres"]].copy()
    pair_movie_df["Genre_List"] = pair_movie_df["Genres"].str.split("|")
    pair_movie_df = pair_movie_df.explode("Genre_List").rename(columns={"Genre_List": "Genre"})
    
    pair_list = []
    for movie_id, group in pair_movie_df.groupby("MovieID"):
        genres = sorted(group["Genre"].unique())
        for pair in combinations(genres, 2):
            pair_list.append({
                "MovieID": movie_id,
                "Genre_Pair": f"{pair[0]} + {pair[1]}"
            })
            
    pair_movie_pairs = pd.DataFrame(pair_list)
    pair_rating_analysis = (
        pair_movie_pairs
        .merge(ratings[["MovieID", "Rating"]], on="MovieID")
        .groupby("Genre_Pair")["Rating"]
        .agg(["count", "mean"])
        .sort_values("count", ascending=False)
    )
    
    # Reliable pairs with >= 500 ratings
    reliable_pairs = (
        pair_rating_analysis[pair_rating_analysis["count"] >= 500]
        .sort_values("mean", ascending=False)
    )
    
    return genre_pairs_count, pair_rating_analysis, reliable_pairs

@st.cache_data(show_spinner=False)
def run_apriori_rules(min_support=0.02, min_confidence=0.3):
    """Run Apriori algorithm on movie genres matrix as implemented in DMT.ipynb."""
    movies, _, _ = load_raw_data()
    genre_matrix = movies["Genres"].str.get_dummies(sep="|").astype(bool)
    
    frequent_genres = apriori(
        genre_matrix,
        min_support=min_support,
        use_colnames=True
    )
    
    if frequent_genres.empty:
        return frequent_genres, pd.DataFrame()
        
    rules = association_rules(
        frequent_genres,
        metric="confidence",
        min_threshold=min_confidence
    )
    
    if rules.empty:
        return frequent_genres, rules
        
    rules = rules.sort_values("lift", ascending=False).reset_index(drop=True)
    
    # Clean display labels
    rules["Antecedents_Str"] = rules["antecedents"].apply(lambda x: ", ".join(list(x)))
    rules["Consequents_Str"] = rules["consequents"].apply(lambda x: ", ".join(list(x)))
    rules["Rule"] = rules["Antecedents_Str"] + " → " + rules["Consequents_Str"]
    
    return frequent_genres, rules

@st.cache_data(show_spinner=False)
def get_pca_analysis():
    """Compute User-Genre rating matrix and 2-component PCA as in DMT.ipynb."""
    movies, ratings, users = load_raw_data()
    df = ratings.merge(movies, on="MovieID")
    genre_df = df.assign(Genre=df["Genres"].str.split("|")).explode("Genre")
    
    user_genre = (
        genre_df
        .merge(users[["UserID", "Age_Group"]], on="UserID")
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
    
    pca_df = pd.DataFrame(
        X_pca,
        columns=["PC1", "PC2"],
        index=user_genre.index
    )
    pca_df["Age_Group"] = user_genre["Age_Group"].values
    
    # Loadings (how each genre projects onto PC1 & PC2)
    loadings = pd.DataFrame(
        pca.components_.T,
        columns=["PC1", "PC2"],
        index=X.columns
    )
    
    return pca_df, pca.explained_variance_ratio_, loadings

@st.cache_data(show_spinner=False)
def get_age_genre_analysis():
    """Generate Age × Genre cross-tabulations and rankings from DMT.ipynb."""
    movies, ratings, users = load_raw_data()
    df = ratings.merge(movies, on="MovieID")
    genre_df = df.assign(Genre=df["Genres"].str.split("|")).explode("Genre")
    
    # Mean rating matrix (Age_Group x Genre)
    genre_age_rating = (
        genre_df
        .merge(users[["UserID", "Age_Group"]], on="UserID")
        .groupby(["Age_Group", "Genre"])["Rating"]
        .mean()
        .unstack()
    )
    
    # Rating count per age group and genre
    age_genre_count = (
        genre_df
        .merge(users[["UserID", "Age_Group"]], on="UserID")
        .groupby(["Age_Group", "Genre"])
        .size()
        .reset_index(name="Movie_Count")
    )
    
    # Top 3 and Top 5 genres per age group
    top3_genres_by_age = (
        age_genre_count
        .sort_values(["Age_Group", "Movie_Count"], ascending=[True, False])
        .groupby("Age_Group")
        .head(3)
    )
    
    top5_genres_by_age = (
        age_genre_count
        .sort_values(["Age_Group", "Movie_Count"], ascending=[True, False])
        .groupby("Age_Group")
        .head(5)
    )
    
    # Overall average rating by age group
    age_ratings = ratings.merge(users[["UserID", "Age_Group"]], on="UserID")
    age_avg_rating = (
        age_ratings.groupby("Age_Group")["Rating"]
        .mean()
        .sort_values(ascending=False)
    )
    
    age_rating_crosstab = pd.crosstab(
        age_ratings["Age_Group"],
        age_ratings["Rating"]
    )
    
    return {
        "genre_age_rating": genre_age_rating,
        "age_genre_count": age_genre_count,
        "top3_genres_by_age": top3_genres_by_age,
        "top5_genres_by_age": top5_genres_by_age,
        "age_avg_rating": age_avg_rating,
        "age_rating_crosstab": age_rating_crosstab
    }

# -------------------------------------------------------------
# UI Styling & Theming Utilities
# -------------------------------------------------------------

def inject_custom_css(dark_mode: bool = False):
    """Inject responsive, modern executive CSS styles into the Streamlit app."""
    bg_color = "#0B0F19" if dark_mode else "#F8FAFC"
    card_bg = "#111827" if dark_mode else "#FFFFFF"
    card_border = "rgba(55, 65, 81, 0.7)" if dark_mode else "rgba(226, 232, 240, 0.9)"
    text_primary = "#F8FAFC" if dark_mode else "#0F172A"
    text_secondary = "#CBD5E1" if dark_mode else "#334155"
    text_muted = "#94A3B8" if dark_mode else "#64748B"
    callout_bg = "#1E293B" if dark_mode else "#F1F5F9"
    badge_bg = "rgba(99, 102, 241, 0.15)" if dark_mode else "rgba(79, 70, 229, 0.08)"
    badge_text = "#818CF8" if dark_mode else "#4F46E5"
    hover_shadow = "0 8px 30px rgba(0, 0, 0, 0.35)" if dark_mode else "0 8px 24px -4px rgba(15, 23, 42, 0.06)"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}
    
    .stApp {{
        background-color: {bg_color};
        color: {text_primary};
    }}

    /* Top header clean up */
    header[data-testid="stHeader"] {{
        background: transparent;
    }}

    /* Global typography */
    h1, h2, h3, h4 {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        color: {text_primary} !important;
        letter-spacing: -0.02em;
    }}
    
    p, span, label, div {{
        color: {text_secondary};
    }}

    /* Modern KPI Cards */
    .kpi-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 14px;
        padding: 20px 22px;
        box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
        margin-bottom: 12px;
    }}
    
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: {hover_shadow};
    }}
    
    .kpi-card::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
    }}
    
    .kpi-label {{
        font-size: 0.775rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: {text_muted};
        margin-bottom: 6px;
    }}
    
    .kpi-value {{
        font-size: 2.1rem;
        font-weight: 800;
        color: {text_primary};
        line-height: 1.15;
        letter-spacing: -0.03em;
        font-feature-settings: "tnum";
    }}
    
    .kpi-subtext {{
        font-size: 0.8rem;
        color: {text_muted};
        margin-top: 6px;
    }}

    /* Analytical Card Wrapper */
    .analysis-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04);
        margin-bottom: 24px;
    }}
    
    .analysis-title {{
        font-size: 1.15rem;
        font-weight: 700;
        color: {text_primary};
        margin-bottom: 4px;
    }}
    
    .analysis-subtitle {{
        font-size: 0.85rem;
        color: {text_muted};
        margin-bottom: 16px;
    }}

    /* Takeaway Callout Box */
    .takeaway-box {{
        background: {callout_bg};
        border-left: 4px solid #4F46E5;
        border-radius: 0 10px 10px 0;
        padding: 16px 18px;
        margin-top: 8px;
        margin-bottom: 12px;
    }}
    
    .takeaway-header {{
        font-size: 0.825rem;
        font-weight: 700;
        color: #4F46E5;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    
    .takeaway-text {{
        font-size: 0.9rem;
        line-height: 1.55;
        color: {text_secondary};
        margin: 0;
    }}

    /* Pill Badges */
    .badge {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        background: {badge_bg};
        color: {badge_text};
        margin-right: 6px;
        margin-bottom: 6px;
    }}
    
    .badge-emerald {{
        background: rgba(16, 185, 129, 0.12);
        color: #10B981;
    }}
    
    .badge-amber {{
        background: rgba(245, 158, 11, 0.12);
        color: #F59E0B;
    }}

    /* Sidebar custom styling */
    section[data-testid="stSidebar"] {{
        background-color: {card_bg};
        border-right: 1px solid {card_border};
    }}
    
    .sidebar-brand {{
        padding: 12px 6px 18px 6px;
        border-bottom: 1px solid {card_border};
        margin-bottom: 16px;
    }}
    
    .sidebar-title {{
        font-size: 1.15rem;
        font-weight: 800;
        color: {text_primary};
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    
    .sidebar-subtitle {{
        font-size: 0.775rem;
        color: {text_muted};
        margin-top: 2px;
    }}

    /* Custom Streamlit tables */
    .stDataFrame {{
        border-radius: 10px;
        overflow: hidden;
    }}

    /* Footer styling */
    .footer-bar {{
        margin-top: 48px;
        padding-top: 20px;
        border-top: 1px solid {card_border};
        text-align: center;
        font-size: 0.8rem;
        color: {text_muted};
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def get_plotly_layout(dark_mode: bool = False, height: int = 420):
    """Return sleek unified Plotly layout options."""
    bg_color = "#111827" if dark_mode else "#FFFFFF"
    paper_color = "#111827" if dark_mode else "#FFFFFF"
    text_color = "#F8FAFC" if dark_mode else "#0F172A"
    grid_color = "rgba(255, 255, 255, 0.08)" if dark_mode else "rgba(15, 23, 42, 0.06)"
    
    layout = dict(
        height=height,
        margin=dict(l=40, r=20, t=40, b=40),
        paper_bgcolor=paper_color,
        plot_bgcolor=bg_color,
        font=dict(
            family="Plus Jakarta Sans, sans-serif",
            color=text_color,
            size=12
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
            zeroline=False,
            color=text_color
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
            zeroline=False,
            color=text_color
        ),
        hoverlabel=dict(
            bgcolor="#1E293B" if dark_mode else "#0F172A",
            font_size=12,
            font_family="Plus Jakarta Sans, sans-serif",
            font_color="#FFFFFF"
        )
    )
    return layout
