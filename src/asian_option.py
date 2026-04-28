"""Asian option MC 가격 산출 모듈.

경로 평균 기초자산 가격을 행사가격과 비교하는 평균가격형(Average Price) Asian option을 구현한다.
산술평균(Arithmetic)과 기하평균(Geometric) 두 가지를 지원한다.

- Arithmetic Asian: 해석해 없음 → MC 필수
- Geometric Asian: 해석해 존재 → MC 검증 기준으로 활용 가능
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, log, sqrt
from typing import Literal

import numpy as np
from scipy.stats import norm

from src.monte_carlo_engine import ContractSpec, MarketAssumption, PricingResult, SimulationSpec
from src.gbm_paths import simulate_paths


AveragingMethod = Literal["arithmetic", "geometric"]


@dataclass(frozen=True)
class AsianSpec:
    """Asian option 추가 설정."""

    averaging: AveragingMethod = "arithmetic"


def price_asian_option(
    market: MarketAssumption,
    contract: ContractSpec,
    sim: SimulationSpec,
    asian: AsianSpec = AsianSpec(),
) -> PricingResult:
    """MC 방식으로 평균가격형 Asian option 가격을 산출한다.

    경로 전체의 평균 가격을 행사가격과 비교해 페이오프를 결정한다.
    """
    # Asian option은 경로 평균이 payoff 입력이므로 terminal price만으로는 계산할 수 없다.
    paths = simulate_paths(market, contract, sim)  # (n_paths, n_steps+1)

    # t=0(S0)을 제외한 t=1..T 구간의 평균 사용
    price_window = paths[:, 1:]

    # 산술평균은 직관적인 평균가격, 기하평균은 로그 평균으로 계산해 해석해 검증에 활용한다.
    if asian.averaging == "arithmetic":
        avg_prices = np.mean(price_window, axis=1)
    else:
        avg_prices = np.exp(np.mean(np.log(price_window), axis=1))

    # 평균가격형 콜/풋 payoff는 평균가격과 행사가격의 차이를 기준으로 결정된다.
    if contract.option_type == "call":
        payoff = np.maximum(avg_prices - contract.strike, 0.0)
    else:
        payoff = np.maximum(contract.strike - avg_prices, 0.0)

    discount = exp(-market.rate * contract.maturity)
    discounted = discount * payoff

    # European MC와 동일한 결과 형식을 사용해 가격, 표준오차, 신뢰구간을 일관되게 비교한다.
    price = float(np.mean(discounted))
    stdev = float(np.std(discounted, ddof=1))
    stderr = stdev / sqrt(sim.n_paths)
    ci_margin = 1.96 * stderr

    return PricingResult(
        price=price,
        stdev=stdev,
        stderr=stderr,
        ci_low=price - ci_margin,
        ci_high=price + ci_margin,
    )


def geometric_asian_analytical(
    market: MarketAssumption,
    contract: ContractSpec,
    sim: SimulationSpec,
) -> float:
    """기하평균 Asian call option의 해석해를 반환한다 (Kemna & Vorst, 1990).

    MC 기하평균 결과의 검증 기준으로 사용한다.
    연속 모니터링 근사를 이산 시간 단계 수(n_steps)로 조정한다.
    """
    S = market.spot
    K = contract.strike
    r = market.rate
    sigma = market.volatility
    T = contract.maturity
    n = sim.n_steps

    # 이산 모니터링 조정 파라미터
    # 평균을 취하면 원 기초자산보다 유효 변동성이 낮아지므로 조정 변동성 sigma_adj를 사용한다.
    sigma_adj = sigma * sqrt((2 * n + 1) / (6 * (n + 1)))
    r_adj = 0.5 * (r - 0.5 * sigma**2 + sigma_adj**2)

    # 조정된 drift/volatility를 Black-Scholes 형태에 대입해 기하평균 Asian call 가격을 얻는다.
    d1 = (log(S / K) + (r_adj + 0.5 * sigma_adj**2) * T) / (sigma_adj * sqrt(T))
    d2 = d1 - sigma_adj * sqrt(T)

    price = exp(-r * T) * (S * exp(r_adj * T) * norm.cdf(d1) - K * norm.cdf(d2))
    return float(price)
