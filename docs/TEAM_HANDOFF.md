# Project Handoff
**Traffic Crash Severity Prediction - San Jose**  
**Date**: March 19, 2026

---

## Where We're At

**Goal**: Predict crash injury severity (0-4 scale) using ML

**Data**:
- SJPD city data: 152,731 vehicle records (2011-2024) - READY
- SWITRS highway data: 116,541 vehicle records (2016-2024) - DOWNLOADED, NOT INTEGRATED

**Status**: EDA complete, highway data downloaded but not merged with SJPD data

---

## What I Just Finished

1. **EDA Complete** - See `notebooks/02_eda.ipynb`
   - Key finding: Severe class imbalance (77% no injury, <2% severe/fatal)
   - Top predictors: Collision type (V=0.31), Primary factor (V=0.28), Sobriety (V=0.24)
   - Rush hour peaks (5-6 PM), U-shaped age risk curve

2. **Downloaded SWITRS Highway Data** (2016-2024)
   - Filtered to San Jose: 56,143 crashes, 116,541 vehicles
   - Files: `data/raw/highway/switrs_crashes_master.csv` and `switrs_parties_master.csv`
   - Scripts: `scripts/download_switrs_data.py`, `scripts/merge_switrs_years.py`

3. **Documented Why SWITRS > TIMS**
   - SWITRS is vehicle-level (matches SJPD structure)
   - TIMS is crash-level (loses driver age, sobriety details)
   - See `docs/CHP_DATA_INTEGRATION.md` for details

---

## What Needs to Be Done

### CRITICAL: Integrate Highway Data
**File to create**: `scripts/integrate_highway_data.py`

**Steps**:
1. Join SWITRS crashes + parties on `CollisionId` to create vehicle-level dataset
2. Map SWITRS columns to SJPD columns (e.g., `PartyAge` → `Age`)
3. Deduplicate: Remove SJPD crashes that appear in SWITRS (match on date+time+location)
4. Merge SJPD + SWITRS into single dataset
5. Output: `data/processed/merged_crash_vehicle_data_with_highways.csv`

**Why this matters**: SJPD has almost no highway coverage (0.2%). SWITRS adds 50K+ highway crashes.

### Then: Feature Engineering & Modeling
1. Create interaction features (age × sobriety, time × weather)
2. Handle class imbalance (SMOTE, class weights)
3. Train baseline models (Logistic Regression, Random Forest, XGBoost)
4. Evaluate with focus on severe/fatal recall (minimize false negatives)

---

## Key Files

**Data**:
- SJPD: `data/processed/merged_crash_vehicle_data.csv`
- SWITRS: `data/raw/highway/switrs_crashes_master.csv` and `switrs_parties_master.csv`

**Notebooks**:
- EDA: `notebooks/02_eda.ipynb`
- Figures: `reports/figures/`

**Docs**:
- Integration strategy: `docs/CHP_DATA_INTEGRATION.md`
- Features: `docs/FEATURES.md`

---

## Quick Facts for Report/Presentation

**Data**: 152K SJPD + 116K SWITRS = 268K total (after integration)

**Severity**: 77% no injury, 15.6% minor, 5.4% moderate, 1.7% severe, 0.2% fatal

**Top Predictors**: Collision type, primary factor, sobriety, lighting

**Temporal**: Peak 5-6 PM, Friday highest, rush hour correlation

**Age Risk**: U-shaped (young 16-25 and elderly 65+ higher risk)

**Challenge**: Severe class imbalance requires SMOTE/class weights

**Why SWITRS**: Vehicle-level data with driver details (TIMS is crash-level only)

---

## Run Commands

```bash
# Re-run EDA
jupyter notebook notebooks/02_eda.ipynb

# Download more SWITRS data (if needed)
python3 scripts/download_switrs_data.py --years 2024 --force

# Merge SWITRS years (already done)
python3 scripts/merge_switrs_years.py
```

---

## Questions?

Check `docs/CHP_DATA_INTEGRATION.md` for detailed integration strategy and schema mapping.
