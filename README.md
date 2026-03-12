# Monte Carlo Pricing Simulation

Portfolio-oriented research repository for derivative pricing under uncertainty. This project is structured to show the full research story first: the market problem, data assumptions, modeling approach, numerical results, and how the work can extend into production finance workflows.

## 1. Problem Definition

Traditional closed-form pricing is efficient when product structure and market assumptions remain simple. In practice, path dependency, custom payoffs, and scenario-based risk analysis quickly make analytic solutions less useful.  
This repository studies how Monte Carlo simulation can be used to estimate derivative value under stochastic price dynamics and how the same framework can scale toward risk, valuation, and strategy applications.

Core research question:

> How reliably can Monte Carlo simulation price a derivative under configurable market assumptions, and what practical insights emerge from the simulation output beyond a single fair value?

## 2. Data

This project is designed to support both synthetic and market-linked workflows.

- `data/raw/`: original inputs such as market snapshots, volatility assumptions, rates, or externally collected reference data
- `data/processed/`: cleaned and transformed datasets ready for modeling
- `data/sample/`: lightweight example inputs and documentation for reproducible demos

Typical inputs for this project:

- underlying asset price
- strike price and maturity
- risk-free rate
- volatility estimate
- simulation count and time-step configuration

## 3. Methodology

The baseline workflow is organized around a reusable pricing pipeline:

1. Define contract and market parameters
2. Generate simulated price paths under a chosen stochastic process
3. Evaluate payoff across simulated paths
4. Discount expected payoff to present value
5. Compare outputs across scenarios, sensitivities, and simulation settings

Expected methodology extensions:

- Geometric Brownian Motion baseline
- variance reduction techniques
- convergence diagnostics
- sensitivity analysis by volatility, maturity, and strike
- comparison with benchmark analytical pricing where available

## 4. Results

Outputs are separated from code and documentation so the repository remains readable and portfolio-ready.

- `outputs/charts/`: convergence plots, path visualizations, scenario comparisons
- `outputs/tables/`: pricing summaries, sensitivity tables, experiment logs
- `outputs/images/`: figures intended for README, reports, or presentation material

Recommended result narrative:

- estimated derivative price
- confidence interval or simulation stability
- parameter sensitivity
- interpretation of model limitations

## 5. Practical Expansion

This repository is intended as a foundation for real finance workflows rather than a one-off class assignment.

Possible extensions:

- exotic option pricing
- structured product payoff simulation
- VaR / Expected Shortfall scenario engines
- stress testing under custom market regimes
- pricing API or dashboard integration for internal tooling

## Repository Structure

```text
monte-carlo-pricing-simulation/
|-- README.md
|-- .gitignore
|-- requirements.txt
|-- docs/
|-- notebooks/
|-- src/
|-- data/
|-- outputs/
|-- references/
|-- presentation/
`-- archive/
```

## Working Principles

- The README acts as the main project document.
- Documentation, code, experiments, and results remain physically separated.
- The structure is reusable for other finance research topics with minimal changes.
- Every addition should strengthen the flow: problem -> data -> methodology -> results -> practical expansion.

## Next Build Targets

- implement a baseline Monte Carlo option pricer in `src/`
- add a reproducible experiment notebook in `notebooks/`
- store result charts and tables under `outputs/`
- summarize findings for portfolio presentation in `docs/` and `presentation/`


## Korean Research Package (KAIST-DFMBA KMS Style Adaptation)

The repository now includes a reusable Korean documentation and experiment package aligned with this repo's structure.

- Core pricing engine: `src/monte_carlo_engine.py`
- Scenario runner: `src/run_pricing_experiment.py`
- Sample scenario data: `data/sample/option_scenarios.csv`
- Korean guide: `docs/kms_adapted_research_package_ko.md`
- Korean workflow note: `references/lecture-notes/monte_carlo_workflow_note_ko.md`

Run:

```bash
python -m src.run_pricing_experiment
```

Outputs:
- `outputs/tables/pricing_results_sample.csv`
- `outputs/charts/pricing_results_sample.png`
