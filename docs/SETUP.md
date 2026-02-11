# Setup Guide

How to get your development environment running.

## Prerequisites

- Python 3.10+
- Conda (Miniconda or Anaconda)
- Git
- A code editor (VS Code recommended)

## Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/traffic-crash-severity.git
cd traffic-crash-severity
```

## Step 2: Create Conda Environment

We use conda to ensure everyone has the same packages.

```bash
# Create environment from file
conda env create -f environment.yml

# Activate it
conda activate crash-severity
```

**If you need to update the environment later:**
```bash
conda env update -f environment.yml
```

## Step 3: Verify Installation

```bash
python -c "import pandas; import sklearn; import numpy; print('All imports OK')"
```

You should see `All imports OK` with no errors.

## Step 4: Test Jupyter

```bash
jupyter lab
```

This should open Jupyter in your browser. Try opening a notebook from `notebooks/`.

## Troubleshooting

### "conda: command not found"
You need to install Miniconda: https://docs.conda.io/en/latest/miniconda.html

### "environment.yml not found"
Make sure you're in the repo root directory (`traffic-crash-severity/`).

### Package conflicts
Try removing and recreating the environment:
```bash
conda deactivate
conda env remove -n crash-severity
conda env create -f environment.yml
```

### Jupyter can't find the kernel
```bash
conda activate crash-severity
python -m ipykernel install --user --name crash-severity
```

## Adding New Packages

If you need a new package:

1. Add it to `environment.yml`
2. Run `conda env update -f environment.yml`
3. Commit the updated `environment.yml`
4. Tell the team in Discord to update their environment

**Do NOT just `pip install` or `conda install` without updating the file.** Otherwise your code won't work for others.

## Editor Setup (VS Code)

Recommended extensions:
- Python
- Jupyter
- GitLens

Set your Python interpreter to the `crash-severity` conda environment:
1. `Cmd/Ctrl + Shift + P`
2. "Python: Select Interpreter"
3. Choose `crash-severity`
