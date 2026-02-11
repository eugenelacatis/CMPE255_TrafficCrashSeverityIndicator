# Traffic Crash Severity Prediction

Predicting injury severity of traffic crashes in San Jose, California using machine learning.

## Project Overview

**Goal:** Build a model that predicts crash injury severity (none → fatal) based on conditions like weather, time of day, road type, and location.

**Deliverables:**
- Trained ML model with evaluation metrics
- Interactive webapp showing crash severity hotspots on a map
- Final paper documenting methodology and findings

**Timeline:** 12 weeks (full semester)

**Team:** 4 members

## Quick Links

| Document | Description |
|----------|-------------|
| [Setup Guide](docs/SETUP.md) | How to install dependencies and run code |
| [Git Workflow](docs/GIT_WORKFLOW.md) | Branching rules and PR process |
| [Feature Definitions](docs/FEATURES.md) | What each feature means |
| [Decision Log](docs/DECISIONS.md) | Why we made certain choices |
| [Meeting Notes](docs/meetings/) | Weekly meeting summaries |

## Data Source

**San Jose Crashes Data:** https://data.sanjoseca.gov/dataset/crashes-data

Files:
- `crashes.csv` - Crash event details (location, time, conditions, severity)
- `vehicles.csv` - Vehicle/driver details per crash

## Target Variable

`injury_severity` - Categorical (5 classes):
| Value | Meaning |
|-------|---------|
| 0 | No injury |
| 1 | Minor injury |
| 2 | Moderate injury |
| 3 | Severe injury |
| 4 | Fatal |

## Project Structure

```
traffic-crash-severity/
├── README.md                 # You are here
├── environment.yml           # Conda environment
├── .gitignore
│
├── data/
│   ├── raw/                  # Original CSVs (committed)
│   └── processed/            # Cleaned data
│
├── notebooks/                # Jupyter notebooks (numbered)
│   ├── 01_data_inspection.ipynb
│   ├── 02_eda.ipynb
│   └── ...
│
├── src/                      # Python modules
│   ├── data/                 # Loading, cleaning, splitting
│   ├── features/             # Feature engineering
│   ├── models/               # Training, prediction
│   └── visualization/        # Plots
│
├── webapp/                   # Streamlit or Flask app
│
├── docs/                     # Documentation
│   ├── SETUP.md
│   ├── GIT_WORKFLOW.md
│   ├── FEATURES.md
│   ├── DECISIONS.md
│   └── meetings/
│
└── reports/                  # Final paper and figures
    └── figures/
```

## Getting Started

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/traffic-crash-severity.git
cd traffic-crash-severity

# Create conda environment
conda env create -f environment.yml
conda activate crash-severity

# Verify setup
python -c "import pandas; import sklearn; print('Setup OK')"
```

See [docs/SETUP.md](docs/SETUP.md) for detailed instructions.

## Status

- [ ] Week 1-2: Data acquisition & EDA
- [ ] Week 3-4: Feature engineering & baseline model
- [ ] Week 5-6: Model experimentation
- [ ] Week 7-8: Tuning & validation
- [ ] Week 9-10: Webapp development
- [ ] Week 11-12: Paper & presentation
