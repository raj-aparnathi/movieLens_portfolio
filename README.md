# MovieLens 1M — Mining Movie Genre & Rating Patterns

An executive-grade Data Mining Techniques (DMT) portfolio dashboard exploring audience behaviors, commercial genre dominance, critical acclaim paradoxes, combinatorial genre pairs, Apriori frequent itemset rules, and unsupervised latent taste segments using PCA.

Built with **Python**, **Streamlit**, **Pandas**, **Plotly**, **Scikit-learn**, and **MLxtend**.

---

## 🚀 Live Demo & How to Run

### 1. Prerequisites
Ensure Python 3.10+ is installed on your system.

### 2. Installation
Navigate to the project directory and install the required dependencies:

```bash
cd movieLens_portfolio
pip install -r requirements.txt
```

### 3. Running the Dashboard
Launch the Streamlit web application:

```bash
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

---

## 📂 Project Architecture

```
movieLens_portfolio/
│
├── app.py                     # Main dashboard entry point & Overview page
├── Design.md                  # Comprehensive visual design system & UX specifications
├── DMT.ipynb                  # Reference Data Mining Techniques notebook
├── ratings.dat                # 1,000,209 ratings across 6,040 users
├── users.dat                  # Demographic profiles for 6,040 users
├── movies.dat                 # 3,883 movie titles with pipe-separated genres
├── README                     # Original GroupLens 1M documentation
├── requirements.txt           # Python dependencies
├── README.md                  # Project overview & running instructions
│
├── pages/
│   ├── dataset.py             # Schema inspection, table previews & demographic decoding
│   ├── eda.py                 # Rating distribution, genre volume, quality & reliable pairs
│   ├── association_rules.py   # Apriori algorithm, Support/Confidence/Lift sliders & charts
│   ├── pca.py                 # 2D User-Genre preference map & component loadings
│   ├── age_genre.py           # Age Cohort × Genre Heatmap & generational preferences
│   ├── findings.py            # Key empirical discoveries & summary scorecard
│   ├── methodology.py         # Visual end-to-end data mining pipeline
│   └── about.py               # Academic context, technology stack, limitations & scope
│
└── utils/
    ├── __init__.py
    └── data_loader.py         # Cached data loading, transformations, Apriori & PCA models
```

---

## 🔬 Implemented Data Mining Techniques

All statistics and visualizations are computed directly from the GroupLens MovieLens 1M dataset with zero simulated or fabricated metrics:

1. **Relational Data Engineering & Ingestion**:
   - Parsed double-colon (`::`) delimiters with `latin-1` encoding.
   - Discretized age keys into 7 standard demographic cohorts (`Under 18` to `56+`).
   - Exploded multi-label genre strings across 18 atomic genres.

2. **Exploratory Data Analysis (EDA)**:
   - Quantified global rating distribution (Mean: `3.58`, Mode: `4 Stars` at 34.9%).
   - Analyzed the commercial volume vs. quality paradox (Comedy & Drama lead volume; Film-Noir leads average rating at `4.08`).
   - Mined statistically reliable genre pairs with ≥ 500 ratings (`Film-Noir + Mystery` holds highest average rating at `4.11`).

3. **Frequent Itemset & Association Rule Mining (Apriori)**:
   - Constructed binary dummy itemsets across catalog genres.
   - Implemented Apriori algorithm with interactive support and confidence thresholds.
   - Mined high-lift rules: **Children's → Animation** achieves a **Lift of 12.38** with **83.2% confidence**.

4. **Principal Component Analysis (PCA)**:
   - Aggregated 1,000,209 ratings into a `6,040 users × 18 genres` rating matrix.
   - Standardized features using `StandardScaler` and reduced to 2 orthogonal components.
   - Explained `26.8%` (PC1) and `11.8%` (PC2) of user preference variance.

5. **Demographic Cross-Tabulation**:
   - Generated Age Group × Genre average rating heatmaps.
   - Identified generational leniency (ratings climb steadily from `3.55` in Under 18 to `3.77` in 56+).

---

## 🎨 Design & Visual Aesthetics

- **Executive Theme**: Custom CSS injection for elevated cards, subtle borders, and smooth hover micro-interactions.
- **Palette**: Slate canvas (`#F8FAFC`), Deep Indigo brand accent (`#4F46E5`), and Electric Violet (`#6366F1`).
- **Dark Mode**: Fully reactive dark mode toggle in the sidebar (`#0B0F19` obsidian background).
- **Responsive Charts**: Custom Plotly templates with unified typography (`Plus Jakarta Sans`), interactive tooltips, and dynamic color scaling.

---

## 📜 Dataset Citation

> F. Maxwell Harper and Joseph A. Konstan. 2015. *The MovieLens Datasets: History and Context.* ACM Transactions on Interactive Intelligent Systems (TiiS) 5, 4, Article 19 (December 2015), 19 pages. DOI: [10.1145/2827872](http://dx.doi.org/10.1145/2827872).
