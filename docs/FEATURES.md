# Feature Definitions

This document defines what each feature means and how it's calculated.

## Target Variable

| Column | Type | Description |
|--------|------|-------------|
| `injury_severity` | int | 0=none, 1=minor, 2=moderate, 3=severe, 4=fatal |

---

## Raw Features (from source data)

These come directly from the San Jose crashes dataset.

### Location Features

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `latitude` | float | GPS latitude | 37.3382 |
| `longitude` | float | GPS longitude | -121.8863 |
| `street_a` | str | Primary street name | "FIRST ST" |
| `street_b` | str | Cross street name | "SANTA CLARA ST" |
| `distance_from_intersection` | float | Feet from nearest intersection | 50.0 |
| `direction_from_intersection` | str | N/S/E/W from intersection | "N" |

### Time Features

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `crash_datetime` | datetime | When crash occurred | 2023-05-15 14:30:00 |
| `crash_date` | date | Date only | 2023-05-15 |
| `crash_time` | time | Time only | 14:30:00 |

### Condition Features

| Column | Type | Description | Values |
|--------|------|-------------|--------|
| `weather` | str | Weather conditions | clear, cloudy, rain, fog, other |
| `road_condition` | str | Road surface | dry, wet, icy, other |
| `lighting` | str | Light conditions | daylight, dark-street lights, dark-no lights, dawn/dusk |
| `road_type` | str | Type of road | highway, arterial, collector, local |

### Collision Features

| Column | Type | Description | Values |
|--------|------|-------------|--------|
| `collision_type` | str | Type of collision | rear-end, head-on, sideswipe, broadside, hit object, pedestrian, bicycle, other |
| `primary_collision_factor` | str | Main cause | speeding, DUI, distracted, right-of-way, other |
| `vehicle_count` | int | Number of vehicles involved | 1, 2, 3, ... |
| `pedestrian_involved` | bool | Was a pedestrian involved | True/False |
| `bicycle_involved` | bool | Was a bicycle involved | True/False |

---

## Engineered Features

These are created from raw features during feature engineering.

### Time-Based Features

| Column | Type | Description | How Calculated |
|--------|------|-------------|----------------|
| `hour` | int | Hour of day (0-23) | Extract from crash_datetime |
| `hour_sin` | float | Cyclical hour encoding | sin(2π × hour / 24) |
| `hour_cos` | float | Cyclical hour encoding | cos(2π × hour / 24) |
| `day_of_week` | int | Day (0=Mon, 6=Sun) | Extract from crash_datetime |
| `is_weekend` | bool | Saturday or Sunday | day_of_week >= 5 |
| `is_rush_hour` | bool | 7-9am or 4-7pm weekday | hour in range AND not weekend |
| `month` | int | Month (1-12) | Extract from crash_datetime |
| `is_night` | bool | Between 8pm and 6am | hour >= 20 OR hour < 6 |

### Location-Based Features

| Column | Type | Description | How Calculated |
|--------|------|-------------|----------------|
| `is_intersection` | bool | At an intersection | distance_from_intersection == 0 |
| `near_highway` | bool | Within X meters of highway | Spatial join with highway data |
| `district` | str | City council district | Spatial join with district boundaries |
| `neighborhood` | str | Neighborhood name | Spatial join with neighborhood data |

### Encoded Features

All categorical features are one-hot encoded:

| Original | Encoded Columns |
|----------|-----------------|
| `weather` | `weather_clear`, `weather_rain`, `weather_fog`, ... |
| `road_condition` | `road_dry`, `road_wet`, `road_icy`, ... |
| `lighting` | `light_day`, `light_dark_lit`, `light_dark_unlit`, ... |
| `collision_type` | `collision_rear_end`, `collision_head_on`, ... |

---

## Notes

### Missing Values

| Column | Missing Value Strategy |
|--------|----------------------|
| `weather` | Fill with "unknown" |
| `road_condition` | Fill with "unknown" |
| `latitude/longitude` | Drop row (can't use without location) |

### Data Quality Issues

Document any issues found during EDA here:

- [ ] TODO: Add issues as discovered

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| YYYY-MM-DD | Initial feature definitions | [Name] |
