"""GBM 전체 경로 생성 모듈.

simulate_terminal_prices()가 만기 가격만 반환하는 것과 달리,
이 모듈은 시간축 전체의 경로 배열을 반환한다.
경로 시각화, Asian option 평균 계산, 경로 의존형 페이오프에 사용된다.
"""

from __future__ import annotations

from math import sqrt

import numpy as np

from src.monte_carlo_engine import MarketAssumption, ContractSpec, SimulationSpec, _validate_inputs


def simulate_paths(
    market: MarketAssumption,
    contract: ContractSpec,
    sim: SimulationSpec,
) -> np.ndarray:
    """GBM 가정 하에서 기초자산 가격 경로 전체를 시뮬레이션한다.

    반환값:
        shape (n_paths, n_steps + 1) 배열.
        열 0은 S0, 열 t는 t번째 시간 단계의 가격.
    """
    _validate_inputs(market, contract, sim)

    # 전체 경로가 필요하므로 각 시간 단계별 drift와 diffusion scale을 먼저 고정한다.
    dt = contract.maturity / sim.n_steps
    drift = (market.rate - 0.5 * market.volatility**2) * dt
    diffusion_scale = market.volatility * sqrt(dt)

    # shock 행렬은 경로 수 x 시간 단계 수 형태이며, 한 행이 하나의 가격 경로를 의미한다.
    rng = np.random.default_rng(sim.seed)
    shocks = rng.standard_normal(size=(sim.n_paths, sim.n_steps))

    # 로그 수익률 누적합으로 경로 생성
    log_increments = drift + diffusion_scale * shocks          # (n_paths, n_steps)
    log_cumsum = np.cumsum(log_increments, axis=1)             # (n_paths, n_steps)

    # S0 열을 앞에 붙여 (n_paths, n_steps+1) 형태로 반환
    log_paths = np.hstack([
        np.full((sim.n_paths, 1), np.log(market.spot)),
        np.log(market.spot) + log_cumsum,
    ])

    return np.exp(log_paths)


def time_grid(contract: ContractSpec, sim: SimulationSpec) -> np.ndarray:
    """경로에 대응하는 시간 격자(0 ~ T)를 반환한다."""
    # 가격 배열 열 개수와 정확히 맞추기 위해 n_steps + 1개 점을 생성한다.
    return np.linspace(0.0, contract.maturity, sim.n_steps + 1)
