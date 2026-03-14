# Monte Carlo Business Risk Analysis Project Foundation

## 1. Project Overview

This mini-project applies Monte Carlo simulation to estimate the monthly profit distribution of a small retail business operating under uncertain market conditions. Rather than relying on a single deterministic forecast, the project models variability in demand, selling price, unit variable cost, and fixed monthly cost to produce a range of possible financial outcomes. The goal is to support lab-report analysis of business risk by quantifying expected profit, downside risk, and how simulation stability changes as the number of iterations increases.

The project is intentionally scoped as a reproducible academic MVP. It prioritizes transparent assumptions, readable project organization, and report-ready outputs that can be explained clearly in a classroom setting while remaining extensible for later scenario expansion.

## 2. MVP Scope

The MVP is limited to four core capabilities:

1. Define a single-business monthly profit model with uncertain financial drivers.
2. Run Monte Carlo simulations for configurable iteration counts such as 100, 1,000, 5,000, and 10,000.
3. Compute core risk metrics including expected profit, variability, loss probability, and percentile outcomes.
4. Produce report-ready tables and charts that show the profit distribution and convergence behavior.

## 3. Business Scenario and Assumptions

### Scenario

The business is a small neighborhood coffee kiosk that sells drinks and light snacks. Monthly profit depends primarily on customer demand, average selling price per unit, average variable cost per unit, and fixed operating expenses.

### Baseline Profit Equation

Monthly profit is defined as:

`profit = (demand x selling_price) - (demand x unit_variable_cost) - fixed_monthly_cost - marketing_spend`

### Core Assumptions

- One simulation run represents one month of operations.
- Demand represents total monthly units sold.
- All units produced are assumed sellable within the month.
- Average price and cost are treated as monthly averages rather than transaction-level values.
- Marketing spend is optional and can be modeled as a fixed amount with a demand uplift effect.
- Seasonality, taxes, staffing variability, and inventory spoilage are excluded from the MVP.

### Suggested Input Distributions

The following distributions are concrete, academically reasonable, and simple enough to explain:

| Variable | Distribution | Example Parameters | Rationale |
|---|---|---:|---|
| Monthly demand | Normal, clipped at 0 | mean = 2,400 units, sd = 350 units | Represents typical month-to-month demand fluctuation around an average |
| Selling price per unit | Triangular | min = 115, mode = 120, max = 128 PHP | Reflects a stable target price with occasional discounts or premium sales mix |
| Unit variable cost | Triangular | min = 48, mode = 52, max = 58 PHP | Captures uncertainty in ingredients, packaging, and small supply changes |
| Fixed monthly cost | Normal, clipped at 0 | mean = 95,000 PHP, sd = 8,000 PHP | Represents rent, salaries, utilities, and overhead variation |
| Marketing spend | Discrete optional scenario | 0 PHP or 12,000 PHP | Allows simple comparison between no-campaign and campaign months |
| Demand uplift from marketing | Uniform | 3% to 10% when marketing is active | Keeps the extension interpretable without making the model complex |

### Notes on Distribution Choice

- Normal is appropriate for demand and fixed cost when variability clusters around an average.
- Triangular is appropriate for selling price and variable cost when minimum, most likely, and maximum values are easier to justify than full historical distributions.
- Clipping negative values prevents non-physical outputs.
- If simplification is preferred in implementation, demand may also be modeled with a triangular distribution instead of a clipped normal distribution.

## 4. Repository Structure

The project should use a simple but scalable layout:

```text
activity-5-business-analysis/
├─ README.md
├─ requirements.txt
├─ pyproject.toml
├─ config/
│  └─ simulation_config.yaml
├─ data/
│  ├─ raw/
│  └─ processed/
├─ src/
│  ├─ __init__.py
│  ├─ models/
│  │  ├─ __init__.py
│  │  └─ business_inputs.py
│  ├─ simulation/
│  │  ├─ __init__.py
│  │  ├─ distributions.py
│  │  └─ monte_carlo.py
│  ├─ analysis/
│  │  ├─ __init__.py
│  │  └─ metrics.py
│  └─ visualization/
│     ├─ __init__.py
│     └─ plots.py
├─ notebooks/
│  └─ exploratory_analysis.ipynb
├─ reports/
│  ├─ figures/
│  └─ tables/
├─ tests/
│  ├─ test_models.py
│  ├─ test_simulation.py
│  └─ test_metrics.py
└─ Docs/
   └─ phase-0-project-foundation.md
```

### Structure Rationale

- `config/` stores reproducible parameters separate from code.
- `src/` isolates the domain model, simulation logic, metrics, and plotting responsibilities.
- `reports/` keeps generated outputs organized for submission use.
- `tests/` supports early validation without overengineering the project.
- `notebooks/` is optional for inspection but not the primary execution path.

## 5. Lightweight Data Model

### Input Model

The input layer should represent the business assumptions for one scenario:

| Field | Type | Example |
|---|---|---|
| `business_name` | string | `Monte Claro Coffee Kiosk` |
| `demand_mean` | float | `2400` |
| `demand_sd` | float | `350` |
| `price_min` | float | `115` |
| `price_mode` | float | `120` |
| `price_max` | float | `128` |
| `variable_cost_min` | float | `48` |
| `variable_cost_mode` | float | `52` |
| `variable_cost_max` | float | `58` |
| `fixed_cost_mean` | float | `95000` |
| `fixed_cost_sd` | float | `8000` |
| `marketing_spend` | float | `12000` |
| `marketing_uplift_min` | float | `0.03` |
| `marketing_uplift_max` | float | `0.10` |

### Simulation Parameters Model

This model should capture reproducibility and experiment setup:

| Field | Type | Example |
|---|---|---|
| `iterations` | int | `5000` |
| `random_seed` | int | `42` |
| `enable_marketing` | bool | `true` |
| `sample_sizes_to_compare` | list[int] | `[100, 1000, 5000, 10000]` |

### Output Metrics Model

Each simulation batch should return summary metrics and optionally raw draws:

| Field | Type | Meaning |
|---|---|---|
| `profit_samples` | array | Simulated monthly profits |
| `expected_profit` | float | Mean of simulated profits |
| `profit_std_dev` | float | Standard deviation of profits |
| `probability_of_loss` | float | Share of runs with profit below zero |
| `p05_profit` | float | 5th percentile profit |
| `p50_profit` | float | Median profit |
| `p95_profit` | float | 95th percentile profit |
| `min_profit` | float | Worst simulated outcome |
| `max_profit` | float | Best simulated outcome |

## 6. Key Performance Indicators

The project should report the following KPIs:

- Expected profit: the average simulated monthly profit.
- Standard deviation of profit: the spread or volatility of outcomes.
- Probability of loss: the likelihood that monthly profit is below zero.
- Percentile outcomes: at minimum the 5th, 50th, and 95th percentiles.
- Range of outcomes: minimum and maximum simulated values for context.
- Convergence behavior: how expected profit and probability of loss stabilize as iteration count increases.

### Recommended Report Interpretation

- Expected profit answers the question, "What is the average financial outcome?"
- Probability of loss answers, "How risky is the business in a bad month?"
- Percentiles answer, "What is a plausible downside and upside range?"
- Convergence results answer, "How many simulation runs are enough for stable conclusions?"

## 7. Experimentation With Different Sample Sizes

The project should explicitly support comparing multiple iteration counts because one learning objective is understanding simulation stability.

### Recommended Sample Sizes

- 100 iterations for a noisy baseline
- 1,000 iterations for a reasonable classroom demonstration
- 5,000 iterations for more stable metrics
- 10,000 iterations for near-MVP reference output

### What to Compare Across Sample Sizes

- Change in expected profit
- Change in probability of loss
- Change in percentile estimates
- Visual smoothing of the profit distribution histogram
- Runtime tradeoff versus result stability

### Expected Academic Insight

Smaller sample sizes should show more variation between runs, while larger sample sizes should produce more stable summary statistics. This lets the report explain why Monte Carlo results improve in reliability as the number of iterations grows.

## 8. Out of Scope

The following items are intentionally excluded from the MVP:

- Multi-branch or multi-product business modeling
- Time-series forecasting across many months
- Real-world database integration or API ingestion
- Optimization of pricing or marketing policies
- Advanced statistical fitting from historical datasets
- Interactive dashboards or web deployment
- Tax, depreciation, financing, or detailed accounting rules

## 9. Expected Deliverables for Later Phases

Later implementation phases should produce:

- A reproducible Python simulation workflow
- Configurable scenario inputs
- A summary table of business risk metrics
- At least two charts: profit distribution and convergence by iteration count
- A short analysis narrative suitable for direct inclusion in a lab report

## 10. Implementation Guidance for Future Phases

To preserve clarity and extensibility:

- Keep simulation logic independent from plotting and reporting code.
- Centralize assumptions in configuration files where possible.
- Use fixed random seeds for demonstrable reproducibility.
- Design functions around a single scenario first, then expand only if later phases require it.
- Store generated figures and tables in dedicated report folders instead of mixing them with source files.

## Commit Message Idea

`docs: add phase 0 foundation for Monte Carlo business risk analysis`
