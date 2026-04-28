"""수렴 분석 모듈.

경로 수(n_paths)를 증가시키면서 MC 가격 추정값과 신뢰구간이
어떻게 안정화되는지 분석한다.

이론적으로 MC 표준오차는 O(1/sqrt(n_paths))로 감소한다.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.monte_carlo_engine import ContractSpec, MarketAssumption, PricingResult, SimulationSpec, price_option


@dataclass(frozen=True)
class ConvergenceRecord:
    """단일 n_paths 수준에서의 수렴 진단 결과."""

    n_paths: int
    price: float
    stderr: float
    ci_low: float
    ci_high: float
    ci_width: float


def run_convergence_analysis(
    market: MarketAssumption,
    contract: ContractSpec,
    base_sim: SimulationSpec,
    path_grid: list[int] | None = None,
) -> pd.DataFrame:
    """path_grid의 각 n_paths 수준에서 MC 가격을 계산해 수렴 테이블을 반환한다.

    Args:
        market: 시장 가정
        contract: 계약 조건
        base_sim: n_steps, seed 등 기본 시뮬레이션 설정 (n_paths는 grid로 대체됨)
        path_grid: 테스트할 경로 수 목록. None이면 기본 격자 사용.

    Returns:
        n_paths, price, stderr, ci_low, ci_high, ci_width 컬럼을 가진 DataFrame.
    """
    if path_grid is None:
        # 작은 경로 수에서 큰 경로 수까지 넓게 잡아 수렴 속도와 계산량 증가를 함께 확인한다.
        path_grid = [100, 500, 1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 100_000]

    records = []
    for n in path_grid:
        # n_paths만 바꾸고 나머지 설정은 고정해 경로 수 변화의 영향만 비교한다.
        sim = SimulationSpec(n_paths=n, n_steps=base_sim.n_steps, seed=base_sim.seed)
        result: PricingResult = price_option(market, contract, sim)
        records.append(
            ConvergenceRecord(
                n_paths=n,
                price=result.price,
                stderr=result.stderr,
                ci_low=result.ci_low,
                ci_high=result.ci_high,
                ci_width=result.ci_high - result.ci_low,
            )
        )

    return pd.DataFrame([vars(r) for r in records])


def theoretical_stderr(
    sample_stdev: float,
    path_grid: list[int],
) -> np.ndarray:
    """표본 표준편차를 기준으로 이론적 표준오차 곡선 O(1/sqrt(n))을 반환한다.

    수렴 플롯에서 실제 수렴 속도와 비교하는 기준선으로 사용한다.
    """
    # 표준오차는 표준편차를 sqrt(N)으로 나눈 값이므로 경로 수가 4배 늘면 절반으로 줄어든다.
    return sample_stdev / np.sqrt(np.array(path_grid, dtype=float))
