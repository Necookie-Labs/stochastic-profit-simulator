# Monte Carlo Business Risk Analysis

This project scaffolds a reproducible Python workflow for Monte Carlo-based business risk analysis. The initial scenario models the monthly profit of Monte Claro Coffee Kiosk under uncertainty in demand, selling price, variable cost, fixed cost, and optional marketing uplift.

## Phase 1 Setup Commands

Run these commands in PowerShell from the project root:

```powershell
git init
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
pip install pytest ruff black
```

If you prefer pinned installs instead of editable mode:

```powershell
pip install numpy pandas matplotlib seaborn scipy pyyaml python-dotenv
pip install pytest ruff black
```

## Recommended Structure

```text
activity-5-business-analysis/
|- README.md
|- pyproject.toml
|- .env.example
|- .gitignore
|- main.py
|- config/
|  \- simulation_config.yaml
|- data/
|  |- raw/
|  \- processed/
|- src/
|  |- __init__.py
|  |- config/
|  |- models/
|  |- simulation/
|  |- analysis/
|  \- visualization/
|- tests/
|- reports/
|  |- figures/
|  \- tables/
|- notebooks/
\- Docs/
```

## Why These Dependencies

- `numpy`: efficient numerical arrays and random sampling for Monte Carlo runs.
- `pandas`: tabular summaries and export-friendly analysis outputs.
- `matplotlib`: baseline plotting for histograms and convergence charts.
- `seaborn`: cleaner statistical chart styling on top of Matplotlib.
- `scipy`: optional support for probability distributions and statistical utilities.
- `pyyaml`: loads reproducible simulation settings from YAML config files.
- `python-dotenv`: reads local environment values without hardcoding them.
- `pytest`: lightweight automated testing for simulation behavior.
- `ruff`: fast linting to keep the codebase consistent as it grows.
- `black`: predictable code formatting with minimal setup.

## Run The Baseline

```powershell
python .\main.py
pytest
```

Expected output:

```text
Monte Carlo Business Risk Analysis environment is ready.
```

## Starter Notes

- The scaffold is intentionally minimal and does not implement simulation logic yet.
- Use `config/simulation_config.yaml` as the single source of default scenario assumptions.
- Store generated charts and tables under `reports/` rather than mixing outputs with source files.

## Commit Message Idea

`chore: scaffold Monte Carlo business risk analysis project`
