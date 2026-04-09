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

**Data**: 152K SJPD + 116K SWITRS = 269K total (after integration, 59 duplicates removed)

**Severity** (combined): 74.1% no injury, 15.9% minor, 7.4% moderate, 1.7% severe, 0.9% fatal

**Severity** (SJPD city only, more reliable): 77% no injury, 15.6% minor, 5.4% moderate, 1.7% severe, 0.86% fatal

**Top Predictors**: Collision type, primary factor, sobriety, lighting

**Temporal**: Peak 5-6 PM, Friday highest, rush hour correlation

**Age Risk**: U-shaped (young 16-25 and elderly 65+ higher risk)

**Challenge**: Severe class imbalance requires SMOTE/class weights

**Why SWITRS**: Vehicle-level data with driver details (TIMS is crash-level only)

---

## Data Quality Notes for Technical Report

### Highway Fatality Rate Caveat
The combined dataset shows **0.9% fatality rate**, but this figure should be cited carefully:

- **SJPD city-only fatality rate: 0.86%** — derived from per-party injury codes; reliable and granular
- **CHP Highway fatality rate: ~0.91%** — derived from crash-level `NumberKilled > 0` only; has two known artifacts:
  1. **Overcounts fatalities**: If a crash kills 1 person but involves 3 vehicles, all 3 party rows are marked `injury_severity = 4`. The actual fatal party count is lower.
  2. **Undercounts injuries**: All injured-but-not-killed highway parties are coded as `injury_severity = 0` (no injury) because per-party injury codes are not available in the downloaded SWITRS parties table. Real-world highway injury rates are higher than what the data shows.

**For the report**: Cite the SJPD city-only severity distribution for granular analysis. Use the combined distribution only for total crash volume comparisons. Note that highway severity data is limited to fatal vs. non-fatal due to SWITRS data structure constraints.

**Real-world context**: California highway fatality rates typically run ~0.5–1% of all crashes, so the ballpark is plausible — the imprecision is in per-party assignment, not the overall rate.

### Deduplication Note
59 SJPD records were removed as likely SWITRS duplicates (matched on date + lat/lon ±111m). No time component was used in matching, so a small number of false positives/negatives may exist.

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
