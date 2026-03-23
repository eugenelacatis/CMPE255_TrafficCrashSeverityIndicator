#!/usr/bin/env python3
"""
Merge SWITRS data from multiple years into master files.
Creates:
  - data/raw/highway/switrs_crashes_master.csv (all years combined)
  - data/raw/highway/switrs_parties_master.csv (all years combined)
"""

import pandas as pd
from pathlib import Path
import glob

PROJECT_ROOT = Path(__file__).parent.parent
HIGHWAY_DIR = PROJECT_ROOT / 'data' / 'raw' / 'highway'

def merge_crashes():
    """Merge all yearly crash files into master file"""
    print("="*80)
    print("Merging SWITRS Crashes")
    print("="*80)
    
    crash_files = sorted(glob.glob(str(HIGHWAY_DIR / 'crashes_*_sanjose.csv')))
    print(f"\nFound {len(crash_files)} crash files:")
    
    dfs = []
    total_records = 0
    
    for file in crash_files:
        year = Path(file).stem.split('_')[1]
        df = pd.read_csv(file, low_memory=False)
        dfs.append(df)
        total_records += len(df)
        print(f"  {year}: {len(df):,} records")
    
    print(f"\nCombining {total_records:,} total crash records...")
    master_df = pd.concat(dfs, ignore_index=True)
    
    output_file = HIGHWAY_DIR / 'switrs_crashes_master.csv'
    master_df.to_csv(output_file, index=False)
    
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"\nSaved: {output_file.name}")
    print(f"  Records: {len(master_df):,}")
    print(f"  Columns: {len(master_df.columns)}")
    print(f"  File size: {file_size_mb:.1f} MB")
    
    return master_df

def merge_parties():
    """Merge all yearly party files into master file"""
    print("\n" + "="*80)
    print("Merging SWITRS Parties")
    print("="*80)
    
    party_files = sorted(glob.glob(str(HIGHWAY_DIR / 'parties_*_sanjose.csv')))
    print(f"\nFound {len(party_files)} party files:")
    
    dfs = []
    total_records = 0
    
    for file in party_files:
        year = Path(file).stem.split('_')[1]
        df = pd.read_csv(file, low_memory=False)
        dfs.append(df)
        total_records += len(df)
        print(f"  {year}: {len(df):,} records")
    
    print(f"\nCombining {total_records:,} total party records...")
    master_df = pd.concat(dfs, ignore_index=True)
    
    output_file = HIGHWAY_DIR / 'switrs_parties_master.csv'
    master_df.to_csv(output_file, index=False)
    
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"\nSaved: {output_file.name}")
    print(f"  Records: {len(master_df):,}")
    print(f"  Columns: {len(master_df.columns)}")
    print(f"  File size: {file_size_mb:.1f} MB")
    
    return master_df

def main():
    print("\n" + "="*80)
    print("SWITRS MASTER FILE CREATION")
    print("="*80)
    print(f"\nSource directory: {HIGHWAY_DIR}")
    
    crashes_df = merge_crashes()
    parties_df = merge_parties()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nTotal San Jose highway crashes (2016-2024): {len(crashes_df):,}")
    print(f"Total parties/vehicles involved: {len(parties_df):,}")
    print(f"Average parties per crash: {len(parties_df)/len(crashes_df):.2f}")
    
    print("\n" + "="*80)
    print("WHY SWITRS > TIMS FOR THIS PROJECT")
    print("="*80)
    print("\n1. GRANULARITY MATCH")
    print("   ✓ SWITRS Parties: VEHICLE-LEVEL (one row per vehicle)")
    print("   ✓ SJPD data: VEHICLE-LEVEL (one row per vehicle)")
    print("   ✓ Perfect match for merging!")
    print("\n   ✗ TIMS: CRASH-LEVEL (one row per crash)")
    print("   ✗ Cannot merge without losing vehicle-level detail")
    
    print("\n2. DRIVER/VEHICLE DETAIL")
    print("   ✓ SWITRS Parties has:")
    print("     - Party age, sex")
    print("     - Sobriety status")
    print("     - Vehicle type, movement")
    print("     - Violation category")
    print("\n   ✗ TIMS only has:")
    print("     - Aggregate counts (total injured/killed)")
    print("     - No per-vehicle driver info")
    
    print("\n3. COMPATIBILITY WITH SJPD")
    print("   ✓ SJPD has: PartyAge, Sobriety, VehicleMake, etc.")
    print("   ✓ SWITRS has: PartyAge, Sobriety, VehicleType, etc.")
    print("   ✓ Can create unified vehicle-level dataset")
    print("\n   ✗ TIMS has: PARTY_COUNT, NUMBER_INJURED")
    print("   ✗ No way to match SJPD's vehicle-level structure")
    
    print("\n4. MODELING IMPACT")
    print("   ✓ SWITRS: Can predict severity based on driver age, sobriety, etc.")
    print("   ✗ TIMS: Can only use crash-level features (time, location)")
    print("   ✗ Loses all driver/vehicle predictive power")
    
    print("\nCONCLUSION: SWITRS Parties + Crashes provides vehicle-level detail")
    print("that matches SJPD structure and preserves modeling capability.")
    print("="*80)

if __name__ == '__main__':
    main()
