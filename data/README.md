# Data Directory

Large CSV files are **not tracked in git** due to GitHub's 100 MB file limit.
Download them from Google Drive and place them in the paths below.

## Google Drive

> **Link**: _(add Google Drive folder link here)_

## Required Files

### Processed (ready to use in notebooks)

| File | Size | Description |
|------|------|-------------|
| `data/processed/merged_crash_vehicle_data.csv` | ~74 MB | SJPD city crashes 2011–2024 (152,731 vehicle records) |
| `data/processed/merged_crash_vehicle_data_with_highways.csv` | ~110 MB | SJPD + CHP highway combined (269,213 vehicle records) |

### Raw Highway (SWITRS)

| File | Size | Description |
|------|------|-------------|
| `data/raw/highway/switrs_crashes_master.csv` | ~24 MB | SWITRS crash-level data, San Jose 2016–2024 |
| `data/raw/highway/switrs_parties_master.csv` | ~28 MB | SWITRS party/vehicle-level data, San Jose 2016–2024 |

### Raw City (SJPD)

| File | Description |
|------|-------------|
| `data/raw/city/crashdata2011-2021.csv` | SJPD crash records 2011–2021 |
| `data/raw/city/crashdata2022-present.csv` | SJPD crash records 2022–present |
| `data/raw/city/vehiclecrashdata2011-2021.csv` | SJPD vehicle records 2011–2021 |
| `data/raw/city/vehiclecrashdata2022-present.csv` | SJPD vehicle records 2022–present |

## Regenerating Processed Files

If you have the raw files, you can regenerate processed files by running the pipeline scripts:

```bash
# Merge SWITRS yearly files → master CSVs
python3 scripts/merge_switrs_years.py

# Integrate highway data with SJPD city data → combined CSV
python3 scripts/integrate_highway_data.py
```

## Notes

- `merged_crash_vehicle_data_with_highways.csv` includes a `data_source` column:
  `SJPD` for city records, `CHP_Highway` for highway records
- Highway records have limited injury severity granularity (see technical report)
