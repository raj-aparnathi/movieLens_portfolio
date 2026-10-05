# Design Specification: MovieLens 1M Analytics Portfolio

## 1. Overview & Vision
The **MovieLens 1M Analytics Portfolio** is a research-grade data mining dashboard designed to present empirical findings from the GroupLens MovieLens 1M dataset. Inspired by modern SaaS analytics platforms (such as Stripe Sigma, Linear, and Datadog), the interface departs from default notebook styling in favor of structured analytical cards, consistent typography, informative metric badges, and side-by-side analytical interpretation.

The goal is to enable recruiters, researchers, and data science peers to immediately grasp:
1. **What data** was mined (1,000,209 ratings, 6,040 users, 3,883 movies, 18 genres).
2. **Which techniques** were applied (Association Rule Mining via Apriori, Principal Component Analysis, Demographic Cross-Tabulation).
3. **What empirical insights** were revealed (e.g., Film-Noir holding the highest mean rating of 4.08, Children's → Animation having a Lift of 12.38).

---

## 2. Color Palette & Thematic Hierarchy

### Light Theme (Default)
- **Background**: Soft Canvas `#F8FAFC` (Slate 50)
- **Card Surface**: Crisp White `#FFFFFF` with ultra-fine border `rgba(226, 232, 240, 0.8)`
- **Sidebar Surface**: `#FFFFFF` / Subtle Slate Tint `#F1F5F9`
- **Primary Brand / Action**: Deep Indigo `#4F46E5` (Hover: `#4338CA`)
- **Secondary Accent**: Electric Violet `#7C3AED` & Cerulean `#0284C7`
- **Highlight / Positive**: Emerald Green `#059669` (for high lift, high rating badges)
- **Warning / Neutral**: Amber `#D97706` (for moderate thresholds)
- **Text Headings (h1, h2, h3)**: Dark Obsidian `#0F172A` (Slate 900)
- **Text Body**: Charcoal Slate `#334155` (Slate 700)
- **Muted / Subtitles**: Heather Slate `#64748B` (Slate 500)
- **Borders & Dividers**: Delicate Grey `#E2E8F0` (Slate 200)

### Dark Theme (Toggleable)
- **Background**: Obsidian Charcoal `#0B0F19`
- **Card Surface**: Dark Navy `#111827` (Gray 900) with border `rgba(55, 65, 81, 0.7)`
- **Sidebar Surface**: `#0F172A`
- **Primary Brand**: Bright Indigo `#6366F1`
- **Text Headings**: `#F8FAFC`
- **Text Body**: `#CBD5E1`
- **Muted Text**: `#94A3B8`
- **Borders**: `#1F2937`

---

## 3. Typography & Micro-Design

- **Primary Font Family**: `'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **Code / Monospace**: `'JetBrains Mono', 'Fira Code', Consolas, monospace`
- **Hierarchy**:
  - **Hero Title**: `2.25rem (36px)`, Weight 700, tracking tight (`-0.025em`)
  - **Section Title / H2**: `1.5rem (24px)`, Weight 600, tracking tight
  - **Card Title / H3**: `1.15rem (18px)`, Weight 600
  - **KPI Metric Value**: `2.2rem (35px)`, Weight 700, tabular numbers
  - **Body / Paragraph**: `0.925rem (14.8px)`, Line height 1.6, Weight 400
  - **Labels / Badges**: `0.75rem (12px)`, Weight 600, uppercase letter-spacing `0.05em`

---

## 4. Layout Architecture & Component Design

### 4.1. Navigation & Modern Sidebar
- **Header**: Minimalist branded avatar `[ML]` + "MovieLens 1M" + subtle pill badge `"DMT Portfolio"`.
- **Navigation Menu**: Segmented list with clean icons and active pill highlight indicator:
  - 🏠 Overview
  - 🗃️ Dataset & Schema
  - 📊 Exploratory Analysis
  - 🔗 Association Rules (Apriori)
  - 🧬 PCA Projection
  - 👥 Age & Genre Analysis
  - 💡 Key Findings
  - ⚙️ Methodology & Pipeline
  - ℹ️ About & Scope
- **Footer**: Dataset metadata badge (`GroupLens Research, Univ. of Minnesota`), quick links, theme indicator.

### 4.2. Metric / KPI Cards
- Standardized 4-column hero grid:
  - Total Users: `6,040` (Demographic breakdown available)
  - Total Movies: `3,883` (18 Distinct Genres)
  - Total Ratings: `1,000,209` (Scale: 1 to 5 Stars)
  - Mean Rating: `3.58` (Standard benchmark)
- Card style: Raised border, soft drop shadow (`box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05)`), top colored accent line or icon badge.

### 4.3. Analysis Cards: Side-by-Side Chart & Insight
Instead of orphan charts spanning the full screen, key visual sections feature a paired layout:
- **Left (65-70% width)**: Interactive Plotly chart with custom clean template, responsive resizing, subtle gridlines (`rgba(226, 232, 240, 0.4)`), and informative hover tooltips.
- **Right (30-35% width)**: **Analytical Takeaway Card** providing:
  - Key observation / metric summary
  - Mining interpretation (e.g., why Film-Noir has high average rating despite lower volume)
  - Practical data mining implication

### 4.4. Tables & Interactive Grids
- Clean tabular styling: alternating row accents, pinned headers, sticky columns, formatting for numbers (e.g., percentages, decimals, integers).
- Association Rules table with sortable columns: `Antecedents`, `Consequents`, `Support (%)`, `Confidence (%)`, `Lift`.

### 4.5. Methodology Visual Pipeline
- Step-by-step horizontal or vertical process cards showing the verified analytical flow:
  `Raw Data (.dat)` → `Encoding & Cleansing` → `Exploratory Profiling` → `Frequent Itemsets (Apriori)` → `Dimensionality Reduction (PCA)` → `Demographic Cross-Tabulation` → `Empirical Takeaways`.

---

## 5. Page-by-Page Content & Structure

1. **Overview**:
   - Hero banner: "MovieLens 1M — Mining Movie Genre & Rating Patterns"
   - 4 Dynamic KPI Cards computed directly from dataset.
   - Quick visual snapshot: Rating Distribution bar & Top 10 Genres by rating count.
   - Executive Summary callout cards.

2. **Dataset**:
   - Structural explanation of `ratings.dat`, `movies.dat`, `users.dat`.
   - Data dimensions, memory footprints, column definitions, and actual parsing parameters (`::` separator, `latin-1`).
   - Interactive preview of each table with row selector.
   - Demographics summary (Age group distribution, Gender ratio).

3. **Exploratory Data Analysis (EDA)**:
   - Rating frequency distribution and % breakdown.
   - Genre popularity (ratings count per genre).
   - Average rating by genre (Film-Noir: 4.08 vs Horror: 3.22).
   - 5-Star rating percentage per genre.
   - Frequent co-occurring genre pairs (e.g. Comedy + Romance, Drama + Romance) and high-rating pairs with >=500 ratings.

4. **Association Rule Mining (Apriori)**:
   - Clear technical explanation: Apriori algorithm applied on movie genre matrices (`min_support=0.02`, `metric='confidence'`, `min_threshold=0.3`).
   - Clarification callout: Rules capture **genre co-occurrence within movie metadata**, not a full collaborative user recommendation engine.
   - Interactive threshold sliders (min support, min confidence) to dynamically inspect generated rules.
   - Top rules ranked by **Lift** (e.g., Children's → Animation: Lift 12.38; Animation → Children's: Lift 12.38; Adventure + Children's → Animation).
   - Interactive Plotly scatter plot (Support vs Confidence sized/colored by Lift) and horizontal bar chart of top rules.

5. **PCA (Dimensionality Reduction)**:
   - Explanation of methodology: Constructing User-Genre rating matrix (6040 users × 18 genres), standardizing with `StandardScaler()`, decomposing with `PCA(n_components=2)`.
   - Variance explained by PC1 and PC2.
   - Interactive 2D scatter plot colored by `Age_Group`.
   - Analytical interpretation: separation of user genre preferences and demographic clustering.

6. **Age & Genre Analysis**:
   - Cross-tabulated heatmap of `Age_Group` vs `Genre` average ratings.
   - Most watched/rated genres per demographic group (Top 3 and Top 5 rankings).
   - Generational rating comparison (e.g., older age groups 56+ giving higher average ratings).

7. **Key Findings**:
   - Curated visual cards highlighting verified empirical discoveries from `DMT.ipynb`.
   - Core metrics table matching Cell 43 & 44.

8. **Methodology Pipeline**:
   - Detailed workflow diagram and explanation of the data mining pipeline.
   - Integrity notice: Highlighting reproducibility and real execution directly from source data files.

9. **About & Academic Context**:
   - Project metadata, author, course info (Data Mining Techniques).
   - Citation of GroupLens Research dataset.
   - Distinct, unambiguous boundary between **"Implemented Techniques"** and **"Future Scope"** (Collaborative Filtering, Matrix Factorization, Deep Hybrid Recommenders).

---

## 6. Implementation Principles
- **No Invented Metrics**: All charts, figures, and insights are driven directly by `ratings.dat`, `movies.dat`, and `users.dat` using the exact notebook logic.
- **Performance & Caching**: All heavy data operations (e.g., parsing 1M ratings, exploding genres, building user matrices) are cached using `@st.cache_data` to ensure sub-second page transitions.
- **Responsive & Clean**: Streamlit custom CSS injection for card containers, metric widgets, pill badges, and typography, overriding default Streamlit plainness with an executive-grade aesthetic.
