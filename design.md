# 🎨 Design System — MovieLens 1M Portfolio

## Design Philosophy

Inspired by the **Segment Studio** dashboard aesthetic — clean, professional, data-focused.
The design prioritises **readability**, **data density**, and a **polished academic** feel
suitable for a professor's review and GitHub showcase.

---

## Color Palette

### Light Mode
| Token              | Value      | Usage                                 |
|--------------------|------------|---------------------------------------|
| `--bg`             | `#f5f6fa`  | Page background                       |
| `--sidebar-bg`     | `#1a1d2e`  | Sidebar background                    |
| `--sidebar-text`   | `#c0c4d6`  | Sidebar link text                     |
| `--sidebar-active`  | `#2ecc71`  | Active nav indicator (teal-green)     |
| `--card-bg`        | `#ffffff`  | Card/panel background                 |
| `--card-border`    | `#e8e9f0`  | Card border                           |
| `--text-primary`   | `#1a1d2e`  | Headings, primary text                |
| `--text-secondary` | `#6b7280`  | Descriptions, captions                |
| `--accent`         | `#2ecc71`  | Buttons, badges, active states        |
| `--accent-hover`   | `#27ae60`  | Accent hover state                    |
| `--kpi-1`          | `#6366f1`  | KPI card 1 (indigo)                   |
| `--kpi-2`          | `#10b981`  | KPI card 2 (emerald)                  |
| `--kpi-3`          | `#f43f5e`  | KPI card 3 (rose)                     |
| `--kpi-4`          | `#0ea5e9`  | KPI card 4 (sky)                      |

### Dark Mode
| Token              | Value      | Change from light                     |
|--------------------|------------|---------------------------------------|
| `--bg`             | `#0f1117`  | Deep dark background                  |
| `--card-bg`        | `#1a1d2e`  | Dark card surface                     |
| `--card-border`    | `#2a2d3e`  | Subtle dark border                    |
| `--text-primary`   | `#e2e8f0`  | Light text on dark                    |
| `--text-secondary` | `#94a3b8`  | Muted text on dark                    |

---

## Typography

| Element        | Font            | Weight | Size   |
|----------------|-----------------|--------|--------|
| Body           | Inter, sans-serif | 400  | 14px   |
| Headings (h1)  | Inter           | 700    | 24px   |
| Headings (h2)  | Inter           | 600    | 20px   |
| Headings (h3)  | Inter           | 600    | 16px   |
| KPI value      | Inter           | 700    | 28px   |
| KPI label      | Inter           | 500    | 13px   |
| Caption        | Inter           | 400    | 12px   |
| Nav item       | Inter           | 500    | 14px   |

---

## Layout

### Grid System
- **Sidebar:** Fixed 250px, full height
- **Main content:** Fluid, padded 32px
- **Cards:** 1–3 column CSS grid, gap 20px
- **Max content width:** None (fills available space)

### Spacing Scale
| Token  | Value | Usage                    |
|--------|-------|--------------------------|
| `xs`   | 4px   | Tight inline spacing     |
| `sm`   | 8px   | Between related elements |
| `md`   | 16px  | Card padding, gaps       |
| `lg`   | 24px  | Section spacing          |
| `xl`   | 32px  | Page padding             |
| `2xl`  | 48px  | Major section breaks     |

---

## Components

### Sidebar Navigation
- Fixed left panel, dark background (#1a1d2e)
- Logo/title at top
- Nav items with SVG icons
- Active item: green left border + green tint background
- Dark mode toggle at bottom
- Subtle hover effect on items

### KPI Cards
- Rounded corners (12px)
- Colored left accent border (4px)
- Large number + small label
- Subtle box-shadow

### Data Cards
- White background, 1px border
- 12px border-radius
- 20px padding
- Optional header with icon

### Tables
- Clean, borderless design
- Header row with light background
- Alternating row tints (optional)
- Rounded container

### Insight Boxes
- Left accent border (4px, colored)
- Light tinted background
- Used for key takeaways

### Charts
- Plotly.js with custom color scheme
- Responsive, fill container width
- Consistent color palette across all charts
- Tooltip styling matches dashboard theme

---

## Chart Color Palette

```
Plotly traces: ['#6366f1','#10b981','#f43f5e','#0ea5e9','#f59e0b','#8b5cf6','#ec4899']
Heatmap:       'YlOrRd'
Sequential:    'Viridis'
```

---

## Page Structure

| Page               | Sidebar Label       | Content                           |
|--------------------|---------------------|-----------------------------------|
| Overview           | 🏠 Overview         | KPI cards, project summary        |
| Dataset            | 📊 Dataset          | File info, samples, preprocessing |
| EDA                | 📈 EDA              | 6 interactive charts              |
| Association Rules  | 🔗 Association Rules| Apriori rules, lift chart          |
| PCA Analysis       | 🧩 PCA Analysis     | PCA scatter, variance             |
| Age & Genre        | 👥 Age & Genre      | Heatmap, top genres by age        |
| Key Findings       | 🔍 Key Findings     | Summary cards                     |
| Methodology        | 🔬 Methodology      | Pipeline diagram                  |
| About              | ℹ️ About            | Tech, limitations, future scope   |

---

## Responsive Behaviour

- Sidebar collapses to icons on screens < 768px
- Cards stack to single column on mobile
- Charts auto-resize via Plotly responsive config

---

## Accessibility

- All interactive elements are focusable
- Color contrast ratio ≥ 4.5:1 for text
- Dark mode respects `prefers-color-scheme`
- Semantic HTML (nav, main, section, article)
