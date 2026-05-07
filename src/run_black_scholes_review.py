"""Black-Scholes 공식 복습용 시나리오 실행 스크립트.

샘플 입력:
    data/sample/black_scholes_review_scenarios.csv

생성 결과:
    outputs/tables/black_scholes_review_results.csv

이 스크립트는 Monte Carlo 경로를 만들지 않는다. 목적은 BS 해석해가 어떤 중간 항
(`d1`, `d2`, 할인계수, 기초자산항, 할인 행사가항)을 거쳐 계산되는지 확인하는 것이다.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.black_scholes_review import build_black_scholes_review_table
from src.config import SAMPLE_DATA_DIR, TABLES_DIR


def load_review_scenarios(path: Path) -> pd.DataFrame:
    """복습용 합성 시나리오 CSV를 읽는다.

    이 입력은 실제 시장 데이터가 아니라 공식을 복습하기 위한 작은 예제다.
    따라서 spot, strike, maturity, rate, volatility가 모두 명시되어야 하며,
    결과 테이블에는 같은 입력값과 중간 계산값을 함께 저장한다.
    """
    return pd.read_csv(path)


def save_review_table(results: pd.DataFrame, output_path: Path) -> None:
    """BS 복습 결과 테이블을 CSV로 저장한다."""
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_path, index=False)


def main() -> None:
    """샘플 시나리오를 실행해 공식 분해 결과를 저장한다."""
    input_path = SAMPLE_DATA_DIR / "black_scholes_review_scenarios.csv"
    output_path = TABLES_DIR / "black_scholes_review_results.csv"

    scenarios = load_review_scenarios(input_path)
    results = build_black_scholes_review_table(scenarios)
    save_review_table(results, output_path)

    # CLI에서 바로 복습 포인트를 확인할 수 있도록 핵심 컬럼만 짧게 출력한다.
    preview_columns = [
        "scenario_id",
        "option_type",
        "d1",
        "d2",
        "stock_leg_value",
        "bond_leg_value",
        "price",
        "delta",
        "vega",
        "put_call_parity_gap",
    ]
    print(f"Black-Scholes 복습 테이블 저장 완료: {output_path}")
    print(results[preview_columns].round(6).to_string(index=False))


if __name__ == "__main__":
    main()
