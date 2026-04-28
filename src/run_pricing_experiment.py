"""시나리오 테이블을 읽어 몬테카를로 가격 산출 결과를 저장하는 실행 스크립트."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.config import CHARTS_DIR, SAMPLE_DATA_DIR, TABLES_DIR
from src.monte_carlo_engine import ContractSpec, MarketAssumption, SimulationSpec, price_option


def load_scenarios(path: Path) -> pd.DataFrame:
    """샘플 시나리오 CSV를 로드한다."""

    # CSV 컬럼명을 그대로 유지해 시나리오 입력값을 명시적으로 매핑한다.
    return pd.read_csv(path)


def run_experiment(df: pd.DataFrame) -> pd.DataFrame:
    """입력 시나리오별 가격을 계산해 결과 데이터프레임으로 반환한다."""

    rows = []
    for _, row in df.iterrows():
        # 한 행의 시장 가정, 계약 조건, 시뮬레이션 설정을 각각 명확한 데이터 구조로 분리한다.
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

        # 결과 테이블은 입력값과 산출값을 함께 남겨 재실행 없이도 조건을 추적할 수 있게 한다.
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

    # errorbar는 시나리오별 추정 가격과 95% 신뢰구간을 한 화면에서 비교하기 위한 가장 단순한 표현이다.
    plt.errorbar(x, y, yerr=yerr, fmt="o", capsize=4)
    plt.title("Monte Carlo Option Price by Scenario (95% CI)")
    plt.xlabel("Scenario ID")
    plt.ylabel("Estimated Price")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def main() -> None:
    # 표준 폴더 구조의 입력/출력 경로를 조합해 어느 위치에서 실행해도 같은 산출물을 만든다.
    input_path = SAMPLE_DATA_DIR / "option_scenarios.csv"
    table_path = TABLES_DIR / "pricing_results_sample.csv"
    chart_path = CHARTS_DIR / "pricing_results_sample.png"

    scenarios = load_scenarios(input_path)
    results = run_experiment(scenarios)

    # outputs 하위 폴더가 비어 있거나 새 클론 상태여도 실행이 실패하지 않도록 생성한다.
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    results.to_csv(table_path, index=False)
    save_chart(results, chart_path)

    print(f"결과 테이블 저장 완료: {table_path}")
    print(f"결과 차트 저장 완료: {chart_path}")


if __name__ == "__main__":
    main()
