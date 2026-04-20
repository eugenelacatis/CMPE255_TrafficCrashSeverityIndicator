# Task 2: Random Forest Model

**Branch:** `random-forest-model`  
**File to create:** `notebooks/04_random_forest.ipynb`  
**Date:** April 20, 2026

---

## Context

Data mining is complete. The project has 269K merged crash records. Your job is to train a Random Forest classifier to predict crash injury severity, evaluate it, and produce charts for the final report. Use the SJPD city-only data (`merged_crash_vehicle_data.csv`) — it has more reliable per-party severity labels than the highway data.

**Data file:** `data/processed/merged_crash_vehicle_data.csv` (on Google Drive — see `data/README.md`)  
**EDA context:** `notebooks/02_eda.ipynb` — top features are CollisionType (V=0.31), PrimaryCollisionFactor (V=0.28), Sobriety (V=0.24), Lighting, Weather  
**Target variable:** `injury_severity` (0=No Injury, 1=Minor, 2=Moderate, 3=Severe, 4=Fatal)

Note: The person doing Task 3 (Naive Bayes) needs your macro-F1 and severe+fatal recall numbers. Share those with them once your notebook is done.

---

## Git Workflow

```bash
git checkout master && git pull origin master
git checkout -b random-forest-model
```

When done: push and open a PR. No checklist section in the PR body.  
**Before committing:** Kernel → Restart & Clear Output, then save.

---

## Important Notes

**Column name casing:** The CSV uses PascalCase, not snake_case. Actual column names:  
`Latitude`, `Longitude`, `CollisionType`, `PrimaryCollisionFactor`, `Sobriety`, `Lighting`, `Weather`, `RoadwaySurface`, `RoadwayCondition`, `VehicleDamage`, `MovementPrecedingCollision`, `Age`, `VehicleCount`, `CrashDateTime`, `injury_severity`  
Always verify with `df.columns.tolist()` after loading.

**Zero coordinates:** Filter `(Latitude == 0) | (Longitude == 0)` before modeling.

**Data file is gitignored:** The CSV is on Google Drive, not in the repo. The notebook must raise a clear error if the file is missing.

---

## Step-by-Step

**Cell 1 — Imports**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import joblib, warnings
warnings.filterwarnings('ignore')

PROJECT_ROOT = Path('..').resolve()
DATA_PATH = PROJECT_ROOT / 'data' / 'processed' / 'merged_crash_vehicle_data.csv'
FIGURES_DIR = PROJECT_ROOT / 'reports' / 'figures'
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
```

**Cell 2 — Load data with guard**
```python
if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Data file not found at {DATA_PATH}\n"
        "Download merged_crash_vehicle_data.csv from Google Drive → data/processed/"
    )

df = pd.read_csv(DATA_PATH, low_memory=False)
print(f"Loaded: {df.shape}")
print(df.columns.tolist())
```

**Cell 3 — Feature engineering**
```python
# Parse datetime and extract time features
df['CrashDateTime'] = pd.to_datetime(df['CrashDateTime'], errors='coerce')
df['hour'] = df['CrashDateTime'].dt.hour
df['day_of_week'] = df['CrashDateTime'].dt.dayofweek
df['month'] = df['CrashDateTime'].dt.month
df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
df['is_rush_hour'] = (
    (~df['is_weekend'].astype(bool)) &
    (df['hour'].isin(list(range(7, 10)) + list(range(16, 19))))
).astype(int)
df['is_night'] = ((df['hour'] >= 20) | (df['hour'] < 6)).astype(int)

# Filter invalid coordinates
df = df.dropna(subset=['Latitude', 'Longitude'])
df = df[(df['Latitude'] != 0) & (df['Longitude'] != 0)]

CAT_FEATURES = [
    'CollisionType', 'PrimaryCollisionFactor', 'Sobriety',
    'Lighting', 'Weather', 'RoadwaySurface', 'RoadwayCondition',
    'VehicleDamage', 'MovementPrecedingCollision'
]
NUM_FEATURES = [
    'Latitude', 'Longitude', 'VehicleCount', 'Age',
    'hour', 'day_of_week', 'month', 'is_weekend', 'is_rush_hour', 'is_night'
]

for col in CAT_FEATURES:
    if col in df.columns:
        df[col] = df[col].fillna('Unknown').astype(str)

le_dict = {}
for col in CAT_FEATURES:
    if col in df.columns:
        le = LabelEncoder()
        df[col + '_enc'] = le.fit_transform(df[col])
        le_dict[col] = le

ENCODED_CATS = [c + '_enc' for c in CAT_FEATURES if c in df.columns]
ALL_FEATURES = ENCODED_CATS + [f for f in NUM_FEATURES if f in df.columns]

model_df = df[ALL_FEATURES + ['injury_severity']].dropna()
print(f"Model dataset shape: {model_df.shape}")
print(f"Class distribution:\n{model_df['injury_severity'].value_counts().sort_index()}")
```

**Cell 4 — Train/test split**
```python
X = model_df[ALL_FEATURES]
y = model_df['injury_severity'].astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Train: {X_train.shape}, Test: {X_test.shape}")
```

**Cell 5 — Train**
```python
rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    class_weight='balanced',
    n_jobs=-1,
    random_state=42
)
rf.fit(X_train, y_train)
print("Training complete.")
```

**Cell 6 — Evaluate**
```python
y_pred = rf.predict(X_test)
SEVERITY_NAMES = ['No Injury', 'Minor', 'Moderate', 'Severe', 'Fatal']
target_names = [SEVERITY_NAMES[i] for i in sorted(y.unique())]

print("Classification Report:")
print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))
```

**Cell 7 — Confusion matrix**
```python
cm = confusion_matrix(y_test, y_pred, labels=sorted(y.unique()))
fig, ax = plt.subplots(figsize=(8, 6))
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=target_names)
disp.plot(ax=ax, colorbar=True, cmap='Blues')
ax.set_title('Random Forest — Confusion Matrix', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(FIGURES_DIR / 'rf_confusion_matrix.png', dpi=150, bbox_inches='tight')
plt.show()
```

**Cell 8 — Feature importance**
```python
importances = rf.feature_importances_
feat_imp = pd.Series(importances, index=ALL_FEATURES).sort_values(ascending=False).head(15)

fig, ax = plt.subplots(figsize=(10, 7))
feat_imp.plot(kind='barh', ax=ax, color='steelblue')
ax.invert_yaxis()
ax.set_title('Random Forest — Top 15 Feature Importances', fontsize=14, fontweight='bold')
ax.set_xlabel('Gini Importance')
plt.tight_layout()
plt.savefig(FIGURES_DIR / 'rf_feature_importance.png', dpi=150, bbox_inches='tight')
plt.show()
```

**Cell 9 — Save model** (optional)
```python
MODEL_DIR = PROJECT_ROOT / 'models'
MODEL_DIR.mkdir(exist_ok=True)
joblib.dump(rf, MODEL_DIR / 'random_forest_model.pkl')
print(f"Model saved.")
```

Add `models/` to `.gitignore` — don't commit the `.pkl`.

**Cell 10 — Summary markdown cell**

Write a markdown cell summarizing:
- Overall macro-F1 score
- Best and worst performing class (by F1)
- Top 3 features from the importance chart

This data is needed by the person doing Task 3 (Naive Bayes comparison table).

---

## Expected Results

- Macro-F1 likely in the 0.35–0.55 range
- Severe (class 3) and Fatal (class 4) recall will be low but nonzero due to `class_weight='balanced'`
- Top features should mirror EDA: CollisionType, PrimaryCollisionFactor, Sobriety

---

## Verification

Kernel → Restart & Run All, confirm no errors. Check `reports/figures/` for `rf_confusion_matrix.png` and `rf_feature_importance.png`.  
**Before committing:** Kernel → Restart & Clear Output, then save.
