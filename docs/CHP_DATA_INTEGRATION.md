# CHP SWITRS Data Integration Strategy

## Overview

The California Highway Patrol maintains the **Statewide Integrated Traffic Records System (SWITRS)**, which contains ALL crashes reported to CHP by local and governmental agencies statewide, including highway crashes under CHP jurisdiction.

## Data Availability

### Source
- **Official Portal**: https://data.ca.gov/dataset/ccrs (California Crash Reporting System)
- **Alternative**: https://tims.berkeley.edu (Transportation Injury Mapping System - UC Berkeley)

### Data Structure
SWITRS provides three relational tables per year:
1. **Crashes** - Event-level data (location, time, conditions, severity)
2. **Parties** - Vehicle/driver-level data (age, sex, sobriety, vehicle type)
3. **InjuredWitnessPassengers** - Victim-level data (injury details)

### Coverage
- **Years Available**: 2001-2025 (updated regularly)
- **Geographic Scope**: Entire state of California
- **Jurisdictions**: CHP (highways) + all local agencies (cities)
- **Update Frequency**: Monthly (provisional), Annual (final)

## Current San Jose Data vs SWITRS

### What We Have (SJPD Data)
- **Source**: `data.sanjoseca.gov`
- **Jurisdiction**: San Jose city streets only
- **Years**: 2011-2024
- **Records**: 152,731 crash-vehicle pairs
- **Highway Coverage**: Minimal (27 records = 0.2%)
  - Only on/off ramps and expressways within city limits
  - Does NOT include I-280, I-880, US-101, SR-87 mainlines

### What SWITRS Adds
- **Highway crashes** in San Jose area (I-280, I-880, US-101, SR-87)
- **Standardized schema** across all CA jurisdictions
- **Additional fields** not in SJPD data
- **Validation** - can cross-check SJPD records against SWITRS

## Integration Benefits

### 1. Complete Geographic Coverage
- Current: City streets only
- With SWITRS: City streets + highways + state routes
- **Impact**: More comprehensive severity prediction model

### 2. Highway-Specific Patterns
- Highway crashes have different characteristics:
  - Higher speeds → more severe injuries
  - Different collision types (rear-end on freeways)
  - Different environmental factors (less pedestrian involvement)
- **Impact**: Better model generalization

### 3. Larger Dataset
- Estimated additional records: 10,000-20,000 highway crashes in San Jose area (2011-2024)
- **Impact**: More training data, especially for severe/fatal classes

### 4. Data Validation
- SWITRS should contain all SJPD crashes (local agencies report to CHP)
- Can identify discrepancies or missing data
- **Impact**: Improved data quality

## Integration Challenges

### 1. Schema Differences
- **SJPD**: Custom field names, local codes
- **SWITRS**: Standardized CHP codes
- **Solution**: Create mapping dictionary for common fields

### 2. Geographic Filtering
- SWITRS covers entire state
- Need to filter to San Jose area only
- **Options**:
  - County filter: Santa Clara County
  - Bounding box: Lat/Lon coordinates
  - City name: "SAN JOSE" in location field

### 3. Duplicate Detection
- SJPD crashes may appear in both datasets
- **Solution**: Match on crash date + location + severity

### 4. Data Volume
- SWITRS files are large (statewide)
- **Solution**: Download only Santa Clara County or filter during load

## Recommended Approach

**Goal**: Seamlessly merge CHP highway data with SJPD city street data to create a complete San Jose crash dataset (2011-2024) covering both city streets and highways.

### Phase 1: Data Acquisition (1 day)
1. Download SWITRS Crashes + Parties tables for **2011-2024** (Santa Clara County)
   - Source: https://data.ca.gov/dataset/ccrs
   - Files needed: Crashes_YYYY.csv, Parties_YYYY.csv for each year
2. Download data dictionary (Raw Data Template)
3. Organize in `data/raw/switrs/` directory

### Phase 2: Schema Analysis & Mapping (1-2 days)
1. **Identify common columns** between SWITRS and SJPD
   - Location: Latitude, Longitude, street names
   - Time: Date, hour, day of week
   - Conditions: Weather, lighting, road surface
   - Collision: Type, severity, factors
   - Vehicle/Driver: Age, sex, sobriety, vehicle type
2. **Create mapping dictionary** for field name differences
3. **Standardize categorical values** (e.g., "Clear" vs "CLEAR")
4. **Document unmapped fields** (unique to each dataset)
5. **Test on 2024 data** to validate mapping accuracy

### Phase 3: Geographic Filtering (1 day)
1. Filter SWITRS to San Jose area using:
   - **Primary**: City name = "SAN JOSE" in location field
   - **Secondary**: Bounding box (Lat: 37.15-37.45, Lon: -122.05--121.70)
   - **Validation**: Cross-check against known San Jose highways
2. Count highway vs city street crashes
3. Verify geographic coverage completeness

### Phase 4: Deduplication (1-2 days)
1. **Identify overlaps**: SJPD crashes that also appear in SWITRS
   - Match criteria: Date + Time + Location (within 100m) + Severity
2. **Keep SJPD version** for duplicates (more detailed local data)
3. **Extract highway-only crashes** from SWITRS
4. Document deduplication statistics

### Phase 5: Seamless Merge (2 days)
1. Harmonize schemas to common column set
2. Add `data_source` column: "SJPD" or "CHP_Highway"
3. Concatenate datasets vertically
4. Validate merged dataset:
   - No duplicate crash IDs
   - Date ranges match (2011-2024)
   - Geographic coverage complete
   - Injury severity distribution reasonable
5. Export to `data/processed/merged_crash_vehicle_data_with_highways.csv`

### Phase 6: Analysis & Documentation (1-2 days)
1. Update EDA notebook with combined dataset
2. Compare statistics: SJPD-only vs SJPD+CHP
3. Analyze highway-specific patterns
4. Train baseline model on both datasets
5. Document findings and recommendations

## Decision Criteria

### Proceed with Full Integration (2011-2024) IF:
- ✅ SWITRS adds >5,000 unique highway crashes across all years
- ✅ Schema overlap is >60% (sufficient common fields)
- ✅ Deduplication accuracy >95%
- ✅ Team has 1-2 weeks for integration work
- ✅ Highway patterns are valuable for model (high-speed crashes)

### Proceed with Partial Integration (2022-2024 only) IF:
- ⚠️ Full integration timeline too long
- ⚠️ Older SWITRS data has schema changes
- ⚠️ Team wants to validate approach on recent data first

### Skip Integration IF:
- ❌ SWITRS adds <1,000 unique records total
- ❌ Schema overlap <40% (too many unmapped fields)
- ❌ Project timeline is tight (<4 weeks remaining)
- ❌ Current 152K records already sufficient for modeling

## Next Steps (Immediate Actions)

### Step 1: Download SWITRS Data (Today)
```bash
# Create directory structure
mkdir -p data/raw/switrs/{crashes,parties}

# Download from https://data.ca.gov/dataset/ccrs
# Files needed for each year 2011-2024:
# - Crashes_YYYY.csv
# - Parties_YYYY.csv
# - Raw Data Template (data dictionary)
```

### Step 2: Schema Intersection Analysis (Tomorrow)
1. Load SWITRS 2024 Crashes + Parties
2. Load SJPD 2024 crashes + vehicles
3. Compare column names and identify:
   - **Exact matches** (same name, same meaning)
   - **Semantic matches** (different name, same meaning)
   - **Unique to SWITRS** (new information)
   - **Unique to SJPD** (will be null for highway crashes)
4. Create mapping table in `docs/SWITRS_SJPD_FIELD_MAPPING.md`

### Step 3: Proof of Concept (Day 3-4)
1. Merge 2024 data only
2. Validate deduplication logic
3. Count highway crashes added
4. Check data quality
5. **Decision point**: If successful, proceed with full 2011-2024 integration

### Step 4: Full Integration (Day 5-7)
1. Apply proven merge logic to all years
2. Create unified dataset
3. Update EDA notebook
4. Document findings

### Step 5: Team Review (Day 8)
1. Present combined dataset statistics
2. Show highway vs city street patterns
3. Discuss modeling implications
4. Update project timeline

## Resources

- CHP SWITRS Portal: https://data.ca.gov/dataset/ccrs
- TIMS (UC Berkeley): https://tims.berkeley.edu
- Data Dictionary: Download from CHP portal (Raw Data Template)
- CHP Annual Reports: https://www.chp.ca.gov/programs-services/services-information/switrs-statewide-integrated-traffic-records-system/

---

**Status**: Research complete, awaiting team decision on integration
**Last Updated**: 2026-03-04
