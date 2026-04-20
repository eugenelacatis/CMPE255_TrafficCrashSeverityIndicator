# Task 1: Interactive Crash Map Website

**Branch:** `crash-map-webapp`  
**File to create:** `webapp/app.py`  
**Date:** April 20, 2026

---

## Context

Data mining is complete. The project has 269K merged crash records with lat/lon and severity labels. Your job is to build a Streamlit app that plots all crash locations on an interactive map of San Jose — crashes cluster at low zoom and expand as you zoom in.

**Data file:** `data/processed/merged_crash_vehicle_data.csv` (on Google Drive — see `data/README.md`)  
**EDA context:** `notebooks/02_eda.ipynb` — top features, severity distribution

---

## Git Workflow

```bash
git checkout master && git pull origin master
git checkout -b crash-map-webapp
```

When done: push and open a PR. No checklist section in the PR body.

---

## Important Notes

**Column name casing:** The CSV uses PascalCase. Relevant columns for this task:  
`Latitude`, `Longitude`, `injury_severity`, `CollisionType`, `Lighting`, `Weather`, `crash_year`

**Zero coordinates:** A small number of records have `Latitude=0` or `Longitude=0`. Filter these out before building the map.

**Data file is gitignored:** The CSV is on Google Drive, not in the repo. The app must handle this gracefully.

---

## What to Build

A Streamlit app with a full-screen Folium map. No sidebar controls — just the map and a color legend below it. Crashes are shown as colored circles, grouped into clusters that expand on zoom.

---

## Step-by-Step

**1. Imports and constants**
```python
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import streamlit.components.v1 as components
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "processed" / "merged_crash_vehicle_data.csv"
SAMPLE_N = 50_000
COLOR_MAP = {0: "green", 1: "beige", 2: "orange", 3: "red", 4: "darkred"}
LABEL_MAP = {0: "No Injury", 1: "Minor", 2: "Moderate", 3: "Severe", 4: "Fatal"}
```

**2. Page config and title**
```python
st.set_page_config(page_title="SJ Crash Map", layout="wide")
st.title("San Jose Traffic Crash Severity Map")
st.markdown("Each marker represents a crash. Clusters expand as you zoom in.")
```

**3. Data loading with missing-file guard**
```python
@st.cache_data
def load_data(path, n):
    if not path.exists():
        return None
    df = pd.read_csv(path, low_memory=False, usecols=[
        "Latitude", "Longitude", "injury_severity",
        "CollisionType", "Lighting", "Weather", "crash_year"
    ])
    df = df.dropna(subset=["Latitude", "Longitude", "injury_severity"])
    df = df[(df["Latitude"] != 0) & (df["Longitude"] != 0)]
    df["injury_severity"] = df["injury_severity"].astype(int)
    if len(df) > n:
        df = df.sample(n=n, random_state=42)
    return df

df = load_data(DATA_PATH, SAMPLE_N)
if df is None:
    st.error(
        "Data file not found. Please download `merged_crash_vehicle_data.csv` "
        "from Google Drive and place it at `data/processed/`."
    )
    st.stop()

st.info(f"Showing {len(df):,} crash records (sampled from full dataset).")
```

**4. Build the Folium map**
```python
m = folium.Map(
    location=[df["Latitude"].mean(), df["Longitude"].mean()],
    zoom_start=12,
    tiles="CartoDB positron"
)
cluster = MarkerCluster(name="Crashes").add_to(m)

for row in df.itertuples():
    sev = int(row.injury_severity)
    folium.CircleMarker(
        location=[row.Latitude, row.Longitude],
        radius=5,
        color=COLOR_MAP.get(sev, "gray"),
        fill=True,
        fill_color=COLOR_MAP.get(sev, "gray"),
        fill_opacity=0.7,
        popup=folium.Popup(
            f"Severity: {LABEL_MAP.get(sev, sev)}<br>"
            f"Type: {getattr(row, 'CollisionType', 'N/A')}<br>"
            f"Lighting: {getattr(row, 'Lighting', 'N/A')}<br>"
            f"Year: {int(getattr(row, 'crash_year', 0))}",
            max_width=200
        )
    ).add_to(cluster)
```

Use `itertuples()` not `iterrows()` — it's 3-5x faster for large loops.

**5. Render and add legend**
```python
components.html(m._repr_html_(), height=650, scrolling=False)

st.markdown("""
<div style="display:flex; gap:16px; margin-top:8px;">
  <span style="color:green">&#9679; No Injury</span>
  <span style="color:#c8a84b">&#9679; Minor</span>
  <span style="color:orange">&#9679; Moderate</span>
  <span style="color:red">&#9679; Severe</span>
  <span style="color:darkred">&#9679; Fatal</span>
</div>
""", unsafe_allow_html=True)
```

Using `st.components.v1.html` with `m._repr_html_()` avoids needing the `streamlit-folium` package — `folium` and `streamlit` are already in `environment.yml`.

---

## Verification

```bash
streamlit run webapp/app.py
```

Expected: browser opens, SJ map appears centered on San Jose, markers cluster at zoom 12, expand on zoom in, clicking a marker shows a popup with severity, collision type, lighting, and year.
