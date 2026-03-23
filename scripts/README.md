# SWITRS Data Download Instructions

## Quick Start

```bash
# Download 2024 data only (test run)
python scripts/download_switrs_data.py --years 2024

# Download all years 2011-2024
python scripts/download_switrs_data.py --years 2011-2024

# Download specific years
python scripts/download_switrs_data.py --years 2022,2023,2024

# Download crashes only (skip parties)
python scripts/download_switrs_data.py --years 2024 --crashes-only

# Force re-download even if files exist
python scripts/download_switrs_data.py --years 2024 --force
```

## What the Script Does

1. **Downloads** SWITRS data from data.ca.gov
2. **Filters** to San Jose geographic area:
   - Bounding box: Lat 37.15-37.45, Lon -122.05 to -121.70
   - City name contains "SAN JOSE"
3. **Reduces file size** by ~95% (180MB → ~5-10MB per year)
4. **Saves** filtered data to `data/raw/switrs/`

## File Size Reduction

| Year | Original Size | Filtered Size | Reduction |
|------|--------------|---------------|-----------|
| 2024 | ~180 MB      | ~5-10 MB      | ~95%      |
| 2023 | ~180 MB      | ~5-10 MB      | ~95%      |
| ...  | ...          | ...           | ...       |

**Total for 2011-2024**: ~2.5 GB → ~100-150 MB

## Output Files

```
data/raw/switrs/
├── crashes_2024_sanjose.csv
├── parties_2024_sanjose.csv
├── crashes_2023_sanjose.csv
├── parties_2023_sanjose.csv
└── ...
```

## Dependencies

```bash
pip install pandas requests tqdm
```

## Notes

- Script automatically filters parties to match San Jose crashes (by CASE_ID)
- Progress bars show download status
- Temporary files are deleted after filtering
- Existing files are skipped unless `--force` is used

## Troubleshooting

**Issue**: Resource IDs not available for older years (2011-2021)

**Solution**: The script currently has resource IDs for 2022-2025. For older years, you'll need to:
1. Visit https://data.ca.gov/dataset/ccrs
2. Find the resource ID in the download URL
3. Add to `RESOURCE_IDS` dictionary in the script

**Issue**: Download fails or times out

**Solution**: Run with `--force` to retry, or download years individually
