#!/usr/bin/env python3
"""
Integrate SWITRS highway data with SJPD city street data.

Steps:
  1. Join SWITRS crashes + parties on CollisionId (vehicle-level)
  2. Map SWITRS columns to SJPD column names
  3. Deduplicate: remove SJPD records that also appear in SWITRS
  4. Append SWITRS highway-only records to SJPD data
  5. Output: data/processed/merged_crash_vehicle_data_with_highways.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SJPD_FILE    = PROJECT_ROOT / 'data' / 'processed' / 'merged_crash_vehicle_data.csv'
CRASHES_FILE = PROJECT_ROOT / 'data' / 'raw' / 'highway' / 'switrs_crashes_master.csv'
PARTIES_FILE = PROJECT_ROOT / 'data' / 'raw' / 'highway' / 'switrs_parties_master.csv'
OUTPUT_FILE  = PROJECT_ROOT / 'data' / 'processed' / 'merged_crash_vehicle_data_with_highways.csv'

# ---------------------------------------------------------------------------
# Severity mapping: SWITRS NumberKilled / NumberInjured → 0-4 scale
# SJPD uses: 0=no injury, 1=minor, 2=moderate, 3=severe, 4=fatal
# ---------------------------------------------------------------------------
def switrs_severity(row):
    """Derive injury_severity (0-4) from SWITRS crash-level injury counts."""
    if row.get('NumberKilled', 0) > 0:
        return 4
    # party-level injury codes in parties table are preferred; fall back to crash totals
    return 0  # will be overridden by party-level logic below


SOBRIETY_MAP = {
    'A': 'Had Not Been Drinking',
    'B': 'Had Been Drinking - Under Influence',
    'C': 'Had Been Drinking - Not Under Influence',
    'D': 'Had Been Drinking - Impairment Unknown',
    'E': 'Under Drug Influence',
    'F': 'Impairment Physical',
    'G': 'Sleepy/Fatigued',
    'H': 'Had Not Been Drinking',   # code H maps to sober in SWITRS docs
}

COLLISION_TYPE_MAP = {
    'A': 'Head On',
    'B': 'Sideswipe',
    'C': 'Rear End',
    'D': 'Broadside',
    'E': 'Hit Object',
    'F': 'Overturned',
    'G': 'Vehicle/Pedestrian',
    'H': 'Other',
}

LIGHTING_MAP = {
    'A': 'Daylight',
    'B': 'Dusk - Dawn',
    'C': 'Dark - Street Light',
    'D': 'Dark - No Street Light',
    'E': 'Dark - Street Light Not Functioning',
}

# SWITRS Weather 1 column stores full words (uppercase), not single-letter codes
WEATHER_MAP = {
    'CLEAR':          'Clear',
    'CLOUDY':         'Cloudy',
    'OVERCAST':       'Cloudy',
    'RAINING':        'Rain',
    'SNOWING':        'Snow',
    'HAILING':        'Snow',
    'HAIL':           'Snow',
    'FOG/VISIBILITY': 'Fog',
    'WIND':           'Wind',
    'OTHER':          'Other',
    'SMOKY':          'Other',
    'SMOKEY':         'Other',
    'HAZY(SMOKE)':    'Other',
    'HEAVY SMOKE':    'Other',
}

ROAD_SURFACE_MAP = {
    'A': 'Dry',
    'B': 'Wet',
    'C': 'Snowy - Icy',
    'D': 'Slippery (Muddy Oily etc.)',
    'E': 'No Unusual Conditions',
}

# Normalize SWITRS MovementPrecCollDescription to match SJPD proper case + spelling
MOVEMENT_NORMALIZE = {
    'Xing Into Opposing Lane': 'Crossing Into Opposing Lane',
    'Entering Trafficd':       'Entering Traffic',
    'Making U Turn':           'Making U-Turn',
    'Travelling Wrong Way':    'Traveling Wrong Way',
    'Passing Other Vehicle':   'Passing Other Vehicles',
}

GENDER_MAP = {
    'M': 'M',
    'F': 'F',
}

# ---------------------------------------------------------------------------
# Step 1: Load data
# ---------------------------------------------------------------------------
def load_data():
    print("=" * 70)
    print("LOADING DATA")
    print("=" * 70)

    print(f"\nLoading SJPD data: {SJPD_FILE.name}")
    sjpd = pd.read_csv(SJPD_FILE, low_memory=False)
    print(f"  Records: {len(sjpd):,}  |  Columns: {len(sjpd.columns)}")

    print(f"\nLoading SWITRS crashes: {CRASHES_FILE.name}")
    crashes = pd.read_csv(CRASHES_FILE, low_memory=False)
    # Strip whitespace from column names (raw file has leading spaces)
    crashes.columns = crashes.columns.str.strip()
    print(f"  Records: {len(crashes):,}  |  Columns: {len(crashes.columns)}")

    print(f"\nLoading SWITRS parties: {PARTIES_FILE.name}")
    parties = pd.read_csv(PARTIES_FILE, low_memory=False)
    parties.columns = parties.columns.str.strip()
    print(f"  Records: {len(parties):,}  |  Columns: {len(parties.columns)}")

    return sjpd, crashes, parties


# ---------------------------------------------------------------------------
# Step 2: Join SWITRS crashes + parties → vehicle-level rows
# ---------------------------------------------------------------------------
def join_switrs(crashes, parties):
    print("\n" + "=" * 70)
    print("JOINING SWITRS CRASHES + PARTIES")
    print("=" * 70)

    # Normalise join key
    crashes['CollisionId'] = crashes['Collision Id'].astype(str).str.strip()
    parties['CollisionId'] = parties['CollisionId'].astype(str).str.strip()

    merged = parties.merge(crashes, on='CollisionId', how='inner', suffixes=('_party', '_crash'))
    print(f"  Joined records (parties × crashes): {len(merged):,}")
    return merged


# ---------------------------------------------------------------------------
# Step 3: Map SWITRS columns → SJPD column names
# ---------------------------------------------------------------------------
def map_to_sjpd_schema(sw):
    print("\n" + "=" * 70)
    print("MAPPING SWITRS COLUMNS TO SJPD SCHEMA")
    print("=" * 70)

    out = pd.DataFrame(index=sw.index)

    # --- Identifiers / source tag ---
    out['data_source'] = 'CHP_Highway'

    # --- Time ---
    # SWITRS: "Crash Date Time" e.g. "1/26/2016 3:45:00 PM"
    dt = pd.to_datetime(sw['Crash Date Time'], errors='coerce')
    out['CrashDateTime'] = dt.dt.strftime('%Y-%m-%d %H:%M:%S')
    out['crash_date']    = dt.dt.strftime('%Y-%m-%d')
    out['crash_year']    = dt.dt.year
    out['crash_month']   = dt.dt.month
    out['crash_day']     = dt.dt.day
    out['crash_hour']    = dt.dt.hour
    out['crash_dayofweek'] = dt.dt.dayofweek   # 0=Mon … 6=Sun

    # --- Location ---
    out['Latitude']  = pd.to_numeric(sw['Latitude_crash'] if 'Latitude_crash' in sw.columns else sw.get('Latitude', np.nan), errors='coerce')
    out['Longitude'] = pd.to_numeric(sw['Longitude_crash'] if 'Longitude_crash' in sw.columns else sw.get('Longitude', np.nan), errors='coerce')
    out['AStreetName'] = sw.get('PrimaryRoad', np.nan)
    out['BStreetName'] = sw.get('SecondaryRoad', np.nan)

    # --- Driver / vehicle ---
    out['Age']  = pd.to_numeric(sw['StatedAge'], errors='coerce')
    out['Sex']  = sw['GenderCode'].map(GENDER_MAP)

    out['Sobriety'] = sw['SobrietyDrugPhysicalCode1'].map(SOBRIETY_MAP).fillna('Impairment Not Known')

    out['MovementPrecedingCollision'] = (
        sw['MovementPrecCollDescription']
        .fillna('Unknown')
        .str.title()
        .replace(MOVEMENT_NORMALIZE)
    )
    out['PartyType']  = sw['PartyType'].fillna('Unknown')
    out['SafetyEquipment'] = sw['SafetyEquipmentDescription'].fillna('Unknown')

    # Vehicle info
    out['VehicleMakeModelType'] = (
        sw['Vehicle1Make'].fillna('') + ' ' +
        sw['Vehicle1Model'].fillna('')
    ).str.strip()
    out['VehicleDirection'] = sw['DirectionOfTravel'].fillna('Unknown')

    # --- Crash conditions ---
    out['CollisionType'] = sw['Collision Type Code'].map(COLLISION_TYPE_MAP).fillna('Other')
    out['Lighting']      = sw['LightingCode'].map(LIGHTING_MAP).fillna('Unknown')
    out['Weather']       = sw['Weather 1'].str.strip().str.upper().map(WEATHER_MAP).fillna('Unknown')
    out['RoadwaySurface'] = sw['RoadwaySurfaceCode'].map(ROAD_SURFACE_MAP).fillna('Unknown')
    out['TrafficControl'] = sw.get('TrafficControlDeviceCode', pd.Series('Unknown', index=sw.index)).fillna('Unknown')

    # --- Severity (vehicle-level) ---
    # Derive from crash-level injury counts — party-level detail not in parties table
    killed   = pd.to_numeric(sw['NumberKilled'],  errors='coerce').fillna(0)
    injured  = pd.to_numeric(sw['NumberInjured'], errors='coerce').fillna(0)

    out['FatalInjuries_crash']    = killed.astype(int)
    out['SevereInjuries_crash']   = 0  # not broken out in SWITRS crash table
    out['ModerateInjuries_crash'] = 0
    out['MinorInjuries_crash']    = injured.astype(int)

    # injury_severity: 4=fatal, else 0 (no party-level injury code in SWITRS parties table)
    out['injury_severity'] = np.where(killed > 0, 4, 0)

    # --- Flags ---
    out['HitAndRunFlag']  = sw['IsHitAndRun'].map({True: True, False: False, 'True': True, 'False': False}).fillna(False)
    out['SpeedingFlag']   = False  # not available in SWITRS parties

    # --- SWITRS-specific passthrough (for dedup & traceability) ---
    out['_switrs_collision_id'] = sw['CollisionId']
    out['_switrs_party_id']     = sw['PartyId'].astype(str)

    print(f"  Mapped columns: {len(out.columns)}")
    print(f"  Rows: {len(out):,}")
    return out


# ---------------------------------------------------------------------------
# Step 4: Deduplicate — remove SJPD rows that also appear in SWITRS
# Match on: crash_date + rounded lat/lon (within ~100 m)
# ---------------------------------------------------------------------------
def deduplicate(sjpd, switrs_mapped):
    print("\n" + "=" * 70)
    print("DEDUPLICATION")
    print("=" * 70)

    PRECISION = 3   # ~111 m at equator

    def dedup_key(df):
        lat = pd.to_numeric(df['Latitude'],  errors='coerce').round(PRECISION).astype(str)
        lon = pd.to_numeric(df['Longitude'], errors='coerce').round(PRECISION).astype(str)
        date = pd.to_datetime(df['CrashDateTime'], errors='coerce').dt.strftime('%Y-%m-%d')
        return date + '|' + lat + '|' + lon

    switrs_keys = set(dedup_key(switrs_mapped).dropna())
    sjpd_keys   = dedup_key(sjpd)

    is_dup = sjpd_keys.isin(switrs_keys)
    n_dups = is_dup.sum()
    print(f"  SJPD records found in SWITRS (duplicates): {n_dups:,}")
    print(f"  SJPD records kept (city-only):             {(~is_dup).sum():,}")

    sjpd_clean = sjpd[~is_dup].copy()
    sjpd_clean['data_source'] = 'SJPD'
    return sjpd_clean, n_dups


# ---------------------------------------------------------------------------
# Step 5: Merge and export
# ---------------------------------------------------------------------------
def merge_and_export(sjpd_clean, switrs_mapped):
    print("\n" + "=" * 70)
    print("MERGING & EXPORTING")
    print("=" * 70)

    # Align columns — use SJPD as the canonical schema
    sjpd_cols = set(sjpd_clean.columns)
    switrs_cols = set(switrs_mapped.columns)

    # Add missing cols to SWITRS side (will be NaN)
    for col in sjpd_cols - switrs_cols:
        switrs_mapped[col] = np.nan

    # Keep only SJPD columns + data_source + traceability cols
    keep_cols = list(sjpd_clean.columns) + [
        c for c in switrs_mapped.columns
        if c.startswith('_switrs') and c not in sjpd_clean.columns
    ]
    switrs_aligned = switrs_mapped[keep_cols]

    combined = pd.concat([sjpd_clean, switrs_aligned], ignore_index=True)
    combined.to_csv(OUTPUT_FILE, index=False)

    file_size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    print(f"\n  Output: {OUTPUT_FILE.name}")
    print(f"  Total records:  {len(combined):,}")
    print(f"  SJPD records:   {(combined['data_source'] == 'SJPD').sum():,}")
    print(f"  Highway records:{(combined['data_source'] == 'CHP_Highway').sum():,}")
    print(f"  File size:      {file_size_mb:.1f} MB")
    return combined


# ---------------------------------------------------------------------------
# Step 6: Summary report
# ---------------------------------------------------------------------------
def print_summary(combined, n_dups):
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\n  Total records after merge: {len(combined):,}")
    print(f"  Duplicates removed:        {n_dups:,}")
    print(f"\n  Severity distribution:")
    sev_counts = combined['injury_severity'].value_counts().sort_index()
    labels = {0: 'No Injury', 1: 'Minor', 2: 'Moderate', 3: 'Severe', 4: 'Fatal'}
    total = len(combined)
    for code, count in sev_counts.items():
        label = labels.get(int(code), f'Code {code}')
        pct = count / total * 100
        print(f"    {code} - {label:<12}: {count:>8,}  ({pct:.1f}%)")

    print(f"\n  Date range: "
          f"{combined['crash_year'].min():.0f} – {combined['crash_year'].max():.0f}")
    print(f"  Output: {OUTPUT_FILE}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("\n" + "=" * 70)
    print("HIGHWAY DATA INTEGRATION")
    print("=" * 70)

    sjpd, crashes, parties = load_data()
    switrs_joined          = join_switrs(crashes, parties)
    switrs_mapped          = map_to_sjpd_schema(switrs_joined)
    sjpd_clean, n_dups     = deduplicate(sjpd, switrs_mapped)
    combined               = merge_and_export(sjpd_clean, switrs_mapped)
    print_summary(combined, n_dups)


if __name__ == '__main__':
    main()
