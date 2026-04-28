"""시나리오 테이블을 읽어 몬테카를로 가격 산출 결과를 저장하는 실행 스크립트."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.config import CHARTS_DIR, SAMPLE_DATA_DIR, TABLES_DIR
from src.monte_carlo_engine import ContractSpec, MarketAssumption, SimulationSpec, price_option


def load_scenarios(path: Path) -> pd.DataFrame:
    """샘플 시나리오 CSV를 로드한다."""

    return pd.read_csv(path)


def run_experiment(df: pd.DataFrame) -> pd.DataFrame:
    """입력 시나리오별 가격을 계산해 결과 데이터프레임으로 반환한다."""

    rows = []
    for _, row in df.iterrows():
        market = MarketAssumption(
            spot=float(row["spot"]),
            rate=float(row["rate"]),
            volatility=float(row["volatility"]),
        )
        contract = ContractSpec(
            strike=float(row["strike"]),
            maturity=float(row["maturity"]),
            option_type=str(row["option_type"]),
        )
        sim = SimulationSpec(
            n_paths=int(row["n_paths"]),
            n_steps=int(row["n_steps"]),
            seed=int(row["seed"]),
        )
        result = price_option(market, contract, sim)

        rows.append(
            {
                "scenario_id": row["scenario_id"],
                "option_type": contract.option_type,
                "spot": market.spot,
                "strike": contract.strike,
                "maturity": contract.maturity,
                "rate": market.rate,
                "volatility": market.volatility,
                "n_paths": sim.n_paths,
                "n_steps": sim.n_steps,
                "price": result.price,
                "stderr": result.stderr,
                "ci_low": result.ci_low,
                "ci_high": result.ci_high,
            }
        )

    return pd.DataFrame(rows)


def save_chart(results: pd.DataFrame, output_path: Path) -> None:
    """시나리오별 가격 및 신뢰구간을 시각화한다."""

    plt.figure(figsize=(10, 5))
    x = results["scenario_id"].astype(str)
    y = results["price"]
    yerr = [y - results["ci_low"], results["ci_high"] - y]

    plt.errorbar(x, y, yerr=yerr, fmt="o", capsize=4)
    plt.title("Monte Carlo Option Price by Scenario (95% CI)")
    plt.xlabel("Scenario ID")
    plt.ylabel("Estimated Price")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def main() -> None:
    input_path = SAMPLE_DATA_DIR / "option_scenarios.csv"
    table_path = TABLES_DIR / "pricing_results_sample.csv"
    chart_path = CHARTS_DIR / "pricing_results_sample.png"

    scenarios = load_scenarios(input_path)
    results = run_experiment(scenarios)

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    results.to_csv(table_path, index=False)
    save_chart(results, chart_path)

    print(f"결과 테이블 저장 완료: {table_path}")
    print(f"결과 차트 저장 완료: {chart_path}")


if __name__ == "__main__":
    main()
