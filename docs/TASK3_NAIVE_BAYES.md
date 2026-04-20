# Task 3: Naive Bayes — A Method That Doesn't Work

**Branch:** `enaive-bayes-analysis`  
**File to create:** `notebooks/05_naive_bayes_analysis.ipynb`  
**Date:** April 20, 2026  
**Prerequisite:** Get the macro-F1 and severe+fatal recall numbers from the person doing Task 2 (Random Forest) — you'll need them for the comparison table.

---

## Context

Data mining is complete. The goal of this notebook is academic: demonstrate that Naive Bayes is a poor fit for this dataset, and explain *theoretically* why — using our EDA findings as evidence. The notebook trains two NB variants, compares them against Random Forest, and explains the 4 failure modes.

**Data file:** `data/processed/merged_crash_vehicle_data.csv` (on Google Drive — see `data/README.md`)  
**EDA context:** `notebooks/02_eda.ipynb` — key finding is strong feature correlations (Cramér's V scores), which directly violates NB's independence assumption  
**Target variable:** `injury_severity` (0=No Injury, 1=Minor, 2=Moderate, 3=Severe, 4=Fatal)

---

## Git Workflow

```bash
git checkout master && git pull origin master
git checkout -b naive-bayes-analysis
```

When done: push and open a PR. No checklist section in the PR body.  
**Before committing:** Kernel → Restart & Clear Output, then save.

---

## Important Notes

**Column name casing:** The CSV uses PascalCase, not snake_case. Relevant columns:  
`Latitude`, `Longitude`, `CollisionType`, `PrimaryCollisionFactor`, `Sobriety`, `Lighting`, `Weather`, `RoadwaySurface`, `RoadwayCondition`, `VehicleCount`, `CrashDateTime`, `injury_severity`  
Always verify with `df.columns.tolist()` after loading.

**Zero coordinates:** Filter `(Latitude == 0) | (Longitude == 0)` before modeling.

**Data file is gitignored:** The CSV is on Google Drive, not in the repo.

---

## Step-by-Step

**Cell 1 — Imports**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.naive_bayes import GaussianNB, CategoricalNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, f1_score
import warnings
warnings.filterwarnings('ignore')

PROJECT_ROOT = Path('..').resolve()
DATA_PATH = PROJECT_ROOT / 'data' / 'processed' / 'merged_crash_vehicle_data.csv'
FIGURES_DIR = PROJECT_ROOT / 'reports' / 'figures'
```

**Cell 2 — Motivation (markdown cell)**

Copy this into a markdown cell:

```
## Why Naive Bayes is a Poor Choice for This Dataset

Naive Bayes (NB) assumes all features are **conditionally independent** given the class label.
The EDA (notebook 02) found this assumption is directly violated by correlated feature pairs:

| Feature Pair | Cramér's V | Interpretation |
|---|---|---|
| CollisionType × injury_severity | 0.31 | Strong association |
| PrimaryCollisionFactor × injury_severity | 0.28 | Moderate-strong |
| Sobriety × injury_severity | 0.24 | Moderate |

Features are also correlated **with each other**:
- Sobriety (DUI) co-occurs with nighttime lighting — these are NOT independent
- Weather (Rain) almost always implies RoadwaySurface (Wet) — near-perfect dependence
- CollisionType (Pedestrian) co-occurs with specific MovementPrecedingCollision values

When features are correlated, NB double-counts evidence, degrading probability estimates.

**Two variants and their specific failure modes:**
1. **GaussianNB**: Assumes each feature follows a Gaussian distribution. Our features are
   categorical (CollisionType, Sobriety, Lighting) — modeling label-encoded integers as
   bell curves is statistically meaningless.
2. **CategoricalNB**: Handles categorical inputs correctly but cannot process continuous
   features (Latitude, Longitude, Age), forcing us to exclude location entirely.
   NB also has no `class_weight` parameter to handle class imbalance.
```

**Cell 3 — Load data with guard**
```python
if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Data file not found at {DATA_PATH}\n"
        "Download merged_crash_vehicle_data.csv from Google Drive → data/processed/"
    )

df = pd.read_csv(DATA_PATH, low_memory=False)
df['CrashDateTime'] = pd.to_datetime(df['CrashDateTime'], errors='coerce')
df['hour'] = df['CrashDateTime'].dt.hour
df['day_of_week'] = df['CrashDateTime'].dt.dayofweek
df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
df['is_rush_hour'] = (
    (~df['is_weekend'].astype(bool)) &
    (df['hour'].isin(list(range(7, 10)) + list(range(16, 19))))
).astype(int)
df['is_night'] = ((df['hour'] >= 20) | (df['hour'] < 6)).astype(int)
df = df[(df['Latitude'] != 0) & (df['Longitude'] != 0)]
```

**Cell 4 — Prepare features for all three models**
```python
CAT_FEATURES = [
    'CollisionType', 'PrimaryCollisionFactor', 'Sobriety',
    'Lighting', 'Weather', 'RoadwaySurface', 'RoadwayCondition'
]
NUM_FEATURES = ['VehicleCount', 'hour', 'day_of_week', 'is_weekend', 'is_rush_hour', 'is_night']

for col in CAT_FEATURES:
    df[col] = df[col].fillna('Unknown').astype(str)

# LabelEncoding for GaussianNB (we know this is wrong — that's the point)
le_dict = {}
for col in CAT_FEATURES:
    le = LabelEncoder()
    df[col + '_le'] = le.fit_transform(df[col])
    le_dict[col] = le

# OrdinalEncoding for CategoricalNB (must be non-negative integers)
oe = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
df[[c + '_oe' for c in CAT_FEATURES]] = oe.fit_transform(df[CAT_FEATURES]).astype(int)
for col in CAT_FEATURES:
    df[col + '_oe'] = df[col + '_oe'].clip(lower=0)

GAUSSIAN_FEATURES = [c + '_le' for c in CAT_FEATURES] + NUM_FEATURES
CATEGORICAL_FEATURES = [c + '_oe' for c in CAT_FEATURES]  # no continuous features
RF_FEATURES = [c + '_le' for c in CAT_FEATURES] + NUM_FEATURES + ['Latitude', 'Longitude']

model_df = df[GAUSSIAN_FEATURES + CATEGORICAL_FEATURES + ['Latitude', 'Longitude', 'injury_severity']].dropna()
y = model_df['injury_severity'].astype(int)

X_g = model_df[GAUSSIAN_FEATURES]
X_c = model_df[CATEGORICAL_FEATURES]
X_rf = model_df[[f for f in RF_FEATURES if f in model_df.columns]]

X_g_train, X_g_test, y_train, y_test = train_test_split(
    X_g, y, test_size=0.2, random_state=42, stratify=y
)
X_c_train = X_c.loc[X_g_train.index]
X_c_test  = X_c.loc[X_g_test.index]
X_rf_train = X_rf.loc[X_g_train.index]
X_rf_test  = X_rf.loc[X_g_test.index]

SEVERITY_NAMES = ['No Injury', 'Minor', 'Moderate', 'Severe', 'Fatal']
target_names = [SEVERITY_NAMES[i] for i in sorted(y.unique())]
```

**Cell 5 — Train and evaluate GaussianNB**
```python
gnb = GaussianNB()
gnb.fit(X_g_train, y_train)
y_pred_gnb = gnb.predict(X_g_test)

print("=== GaussianNB Classification Report ===")
print(classification_report(y_test, y_pred_gnb, target_names=target_names, zero_division=0))
```

**Cell 6 — Train and evaluate CategoricalNB**
```python
cnb = CategoricalNB(alpha=1.0)
cnb.fit(X_c_train, y_train)
y_pred_cnb = cnb.predict(X_c_test)

print("=== CategoricalNB Classification Report ===")
print(classification_report(y_test, y_pred_cnb, target_names=target_names, zero_division=0))
print("\nNote: CategoricalNB excludes Latitude, Longitude, and Age entirely.")
```

**Cell 7 — Train RF for comparison**
```python
rf = RandomForestClassifier(n_estimators=100, class_weight='balanced', n_jobs=-1, random_state=42)
rf.fit(X_rf_train, y_train)
y_pred_rf = rf.predict(X_rf_test)

print("=== Random Forest Classification Report (for comparison) ===")
print(classification_report(y_test, y_pred_rf, target_names=target_names, zero_division=0))
```

**Cell 8 — Comparison table**
```python
def macro_f1(y_true, y_pred):
    return round(f1_score(y_true, y_pred, average='macro', zero_division=0), 3)

def severe_fatal_recall(y_true, y_pred):
    mask = y_true.isin([3, 4])
    if mask.sum() == 0:
        return 0.0
    return round((pd.Series(y_pred)[mask.values] == y_true[mask].values).mean(), 3)

results = {
    'GaussianNB': {
        'Macro F1': macro_f1(y_test, y_pred_gnb),
        'Severe+Fatal Recall': severe_fatal_recall(y_test, y_pred_gnb),
        'Uses Location Features': 'Yes (meaninglessly)',
        'Handles Categoricals Correctly': 'No (treats as numeric)',
        'Handles Class Imbalance': 'No',
    },
    'CategoricalNB': {
        'Macro F1': macro_f1(y_test, y_pred_cnb),
        'Severe+Fatal Recall': severe_fatal_recall(y_test, y_pred_cnb),
        'Uses Location Features': 'No (excluded)',
        'Handles Categoricals Correctly': 'Yes',
        'Handles Class Imbalance': 'No',
    },
    'Random Forest': {
        'Macro F1': macro_f1(y_test, y_pred_rf),
        'Severe+Fatal Recall': severe_fatal_recall(y_test, y_pred_rf),
        'Uses Location Features': 'Yes',
        'Handles Categoricals Correctly': 'Yes (encoded)',
        'Handles Class Imbalance': 'Yes (class_weight=balanced)',
    },
}

comparison_df = pd.DataFrame(results).T
display(comparison_df)
```

**Cell 9 — Side-by-side confusion matrices**
```python
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for ax, (name, y_pred) in zip(axes, [
    ('GaussianNB', y_pred_gnb),
    ('CategoricalNB', y_pred_cnb),
    ('Random Forest', y_pred_rf),
]):
    cm = confusion_matrix(y_test, y_pred, labels=sorted(y.unique()))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=target_names)
    disp.plot(ax=ax, colorbar=False, cmap='Blues')
    ax.set_title(name, fontsize=12, fontweight='bold')
    ax.tick_params(axis='x', rotation=30)

plt.suptitle('Confusion Matrix Comparison: NB vs Random Forest', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(FIGURES_DIR / 'nb_vs_rf_confusion_matrices.png', dpi=150, bbox_inches='tight')
plt.show()
```

**Cell 10 — Theoretical explanation (markdown cell)**

Copy this into a markdown cell:

```
## Why Naive Bayes Fails: Theoretical Analysis

### 1. Independence Assumption Violated
The EDA found multiple feature pairs that co-vary strongly:

- **Sobriety × Lighting**: DUI crashes (Sobriety = "Under Influence") disproportionately
  occur at night. These are nearly dependent features — NB treats them as independent,
  effectively double-counting the nighttime DUI signal.
- **Weather × RoadwaySurface**: Rain weather almost perfectly predicts Wet road surface.
  NB multiplies P(Rain | y) × P(Wet | y), which massively over-weights this evidence.
- **CollisionType × PrimaryCollisionFactor**: Pedestrian collisions cluster tightly with
  specific primary factors, violating the independence assumption.

### 2. GaussianNB Distribution Mismatch
GaussianNB models P(feature | class) as a bell curve. For label-encoded categoricals
(e.g., CollisionType encoded 0–7), this fits a Gaussian over an unordered discrete set.
The resulting probability estimates are numerically computed but statistically meaningless.

### 3. CategoricalNB's Feature Gap
CategoricalNB cannot accept continuous inputs. This forces us to drop:
- **Latitude/Longitude**: Removes all location-based signal (road type, intersection risk)
- **Age**: Removes the U-shaped age risk curve identified in EDA
- **VehicleCount**: Removes multi-vehicle collision signal

### 4. No Class Imbalance Handling
RandomForestClassifier has `class_weight='balanced'`, which inversely weights each class
by its frequency, dramatically improving minority-class (Severe, Fatal) recall.
Naive Bayes has no equivalent parameter — it predicts the majority class by default.

### Conclusion
Naive Bayes achieves low macro-F1 on this dataset because: (1) the independence
assumption is violated by multiple correlated feature pairs found in EDA, (2) GaussianNB's
distributional assumption is invalid for categorical features, (3) CategoricalNB cannot
utilize the most spatially and demographically informative continuous features, and
(4) neither variant handles the severe class imbalance present in crash severity data.
Random Forest avoids all four failure modes.
```

---

## Expected Results

- GaussianNB macro-F1: ~0.15–0.25
- CategoricalNB macro-F1: slightly higher but still worse than RF
- Random Forest macro-F1: ~0.40–0.55
- Both NB variants will have near-zero recall on Severe and Fatal classes

---

## Verification

Kernel → Restart & Run All. The comparison table should clearly show RF > both NB variants on macro-F1 and severe+fatal recall. Check `reports/figures/` for `nb_vs_rf_confusion_matrices.png`.  
**Before committing:** Kernel → Restart & Clear Output, then save.
