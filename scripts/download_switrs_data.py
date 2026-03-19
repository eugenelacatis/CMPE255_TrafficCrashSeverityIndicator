#!/usr/bin/env python3
"""
Download and filter SWITRS crash data for San Jose area (2011-2024)

This script downloads CHP SWITRS data from data.ca.gov and filters it to
San Jose geographic area to reduce file size from ~180MB to ~5-10MB per year.

Usage:
    python scripts/download_switrs_data.py --years 2024
    python scripts/download_switrs_data.py --years 2011-2024
    python scripts/download_switrs_data.py --years 2022,2023,2024
"""

import argparse
import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import time

PROJECT_ROOT = Path(__file__).parent.parent
SWITRS_DIR = PROJECT_ROOT / 'data' / 'raw' / 'highway'
SWITRS_DIR.mkdir(parents=True, exist_ok=True)

SAN_JOSE_BOUNDS = {
    'lat_min': 37.15,
    'lat_max': 37.45,
    'lon_min': -122.05,
    'lon_max': -121.70
}

SWITRS_URLS = {
    'crashes': 'https://data.ca.gov/dataset/80c6a49d-c6b3-40ba-86d8-379c9741b4be/resource/{resource_id}/download/hq1d-p-app52dopendataexport{year}crashes.csv',
    'parties': 'https://data.ca.gov/dataset/80c6a49d-c6b3-40ba-86d8-379c9741b4be/resource/{resource_id}/download/hq1d-p-app52dopendataexport{year}parties.csv'
}

RESOURCE_IDS = {
    2024: {'crashes': 'f775df59-b89b-4f82-bd3d-8807fa3a22a0', 'parties': '93892d36-017b-4a2a-bc0b-f1f385060b96'},
    2023: {'crashes': '436642c0-cd04-4a4c-b45e-564b66437476', 'parties': '84376be5-548b-44e3-8ebc-73e8a2ca9945'},
    2022: {'crashes': '7828780b-117b-455e-9275-986ad3ffde50', 'parties': '9ef51178-51cb-4939-9344-2d0907740580'},
    2021: {'crashes': 'd08692e2-6d36-487e-bca0-28cd127a626f', 'parties': '754fe00c-f3bf-4f2f-80d0-ed4aa7b89b77'},
    2020: {'crashes': 'a2e0605d-0695-4bce-806d-4d0dda7ace68', 'parties': 'ebfed5da-82d6-4af2-bf40-b9516d7935a9'},
    2019: {'crashes': '2b4c7d03-e684-435e-80da-17935de9499f', 'parties': '1a06775e-7d4a-4574-b3d4-f815d02d236a'},
    2018: {'crashes': 'a4b57216-5110-43d3-884c-d95366b19158', 'parties': '42f3f3d1-c130-4ebc-9536-98bf7880b0b9'},
    2017: {'crashes': '4784664d-b7cf-4427-af25-7c7307bad56c', 'parties': 'e8c625e8-674a-49f2-abe9-405267613045'},
    2016: {'crashes': '3d5f2586-cf68-4213-aa1c-60df37399d10', 'parties': '2e8e3d81-4615-4b8e-ab7f-408f10f64bba'},
}


def download_file(url, output_path, chunk_size=8192):
    """Download file with progress bar"""
    print(f"Downloading from: {url}")
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    with open(output_path, 'wb') as f, tqdm(
        desc=output_path.name,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            f.write(chunk)
            pbar.update(len(chunk))
    
    return output_path


def filter_to_san_jose(df, data_type='crashes'):
    """Filter dataframe to San Jose geographic area using city name"""
    original_count = len(df)
    
    if data_type == 'crashes':
        possible_city_cols = ['\tCity Name', 'City Name', 'CITY', 'CITY_NAME']
        city_col = None
        
        for col in possible_city_cols:
            if col in df.columns:
                city_col = col
                break
        
        if city_col:
            filtered_df = df[df[city_col].str.upper().str.contains('SAN JOSE', na=False)].copy()
        else:
            print(f"Warning: No city column found in {df.columns.tolist()[:10]}. Keeping all data.")
            return df
    else:
        return df
    
    filtered_count = len(filtered_df)
    reduction_pct = (1 - filtered_count / original_count) * 100 if original_count > 0 else 0
    
    print(f"  Filtered {data_type}: {original_count:,} → {filtered_count:,} records ({reduction_pct:.1f}% reduction)")
    
    return filtered_df


def download_and_filter_year(year, data_types=['crashes', 'parties'], force=False):
    """Download and filter SWITRS data for a specific year"""
    print(f"\n{'='*80}")
    print(f"Processing Year: {year}")
    print('='*80)
    
    if year not in RESOURCE_IDS:
        print(f"Warning: Resource IDs not available for {year}. Skipping.")
        print(f"Available years: {sorted(RESOURCE_IDS.keys())}")
        return
    
    crash_ids = []
    
    for data_type in data_types:
        resource_id = RESOURCE_IDS[year][data_type]
        url = SWITRS_URLS[data_type].format(resource_id=resource_id, year=year)
        
        temp_file = SWITRS_DIR / f'temp_{data_type}_{year}.csv'
        output_file = SWITRS_DIR / f'{data_type}_{year}_sanjose.csv'
        
        if output_file.exists() and not force:
            print(f"\n{output_file.name} already exists. Skipping download.")
            continue
        
        try:
            print(f"\nDownloading {data_type} for {year}...")
            download_file(url, temp_file)
            
            print(f"Loading and filtering {data_type}...")
            df = pd.read_csv(temp_file, low_memory=False)
            
            if data_type == 'crashes':
                filtered_df = filter_to_san_jose(df, data_type='crashes')
                crash_id_col = 'Collision Id' if 'Collision Id' in filtered_df.columns else 'CASE_ID'
                crash_ids = filtered_df[crash_id_col].unique() if crash_id_col in filtered_df.columns else []
            else:
                party_id_col = 'CollisionId' if 'CollisionId' in df.columns else 'CASE_ID'
                if len(crash_ids) > 0 and party_id_col in df.columns:
                    print(f"  Filtering parties to match San Jose crashes...")
                    original_count = len(df)
                    filtered_df = df[df[party_id_col].isin(crash_ids)].copy()
                    filtered_count = len(filtered_df)
                    reduction_pct = (1 - filtered_count / original_count) * 100
                    print(f"  Filtered parties: {original_count:,} → {filtered_count:,} records ({reduction_pct:.1f}% reduction)")
                else:
                    print(f"  Warning: No crash IDs to filter parties. Keeping all data.")
                    filtered_df = df
            
            print(f"Saving filtered data to {output_file.name}...")
            filtered_df.to_csv(output_file, index=False)
            
            original_size = temp_file.stat().st_size / (1024 * 1024)
            filtered_size = output_file.stat().st_size / (1024 * 1024)
            print(f"  File size: {original_size:.1f} MB → {filtered_size:.1f} MB ({(1-filtered_size/original_size)*100:.1f}% reduction)")
            
            temp_file.unlink()
            
        except Exception as e:
            print(f"Error processing {data_type} for {year}: {e}")
            if temp_file.exists():
                temp_file.unlink()
            continue
        
        time.sleep(1)


def parse_years(years_arg):
    """Parse year argument (e.g., '2024', '2011-2024', '2022,2023,2024')"""
    if '-' in years_arg:
        start, end = map(int, years_arg.split('-'))
        return list(range(start, end + 1))
    elif ',' in years_arg:
        return [int(y.strip()) for y in years_arg.split(',')]
    else:
        return [int(years_arg)]


def main():
    parser = argparse.ArgumentParser(description='Download and filter SWITRS data for San Jose')
    parser.add_argument('--years', type=str, default='2024',
                       help='Years to download (e.g., 2024, 2011-2024, 2022,2023,2024)')
    parser.add_argument('--force', action='store_true',
                       help='Force re-download even if files exist')
    parser.add_argument('--crashes-only', action='store_true',
                       help='Download crashes only (skip parties)')
    
    args = parser.parse_args()
    
    years = parse_years(args.years)
    data_types = ['crashes'] if args.crashes_only else ['crashes', 'parties']
    
    print(f"SWITRS Data Download Script")
    print(f"Years: {years}")
    print(f"Data types: {data_types}")
    print(f"Output directory: {SWITRS_DIR}")
    print(f"Geographic filter: City name contains 'SAN JOSE'")
    
    for year in years:
        download_and_filter_year(year, data_types=data_types, force=args.force)
    
    print(f"\n{'='*80}")
    print("Download complete!")
    print(f"Filtered files saved to: {SWITRS_DIR}")
    print('='*80)


if __name__ == '__main__':
    main()
