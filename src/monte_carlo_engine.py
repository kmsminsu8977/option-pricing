"""몬테카를로 기반 옵션 가격 산출 엔진.

이 모듈은 연구 저장소에서 반복적으로 사용할 수 있는 최소 단위의 가격 산출 로직을 제공한다.
- 기초자산 경로 생성(GBM)
- 만기 페이오프 평가(유럽형 콜/풋)
- 현재가 할인 및 신뢰구간 추정
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, sqrt
from typing import Literal

import numpy as np


@dataclass(frozen=True)
class MarketAssumption:
    """시장 가정 입력값.

    Attributes:
        spot: 현재 기초자산 가격(S0)
        rate: 무위험 이자율(r)
        volatility: 연율 변동성(sigma)
    """

    spot: float
    rate: float
    volatility: float


@dataclass(frozen=True)
class ContractSpec:
    """파생상품 계약 조건.

    Attributes:
        strike: 행사가격(K)
        maturity: 잔존만기(년)
        option_type: 옵션 유형(call 또는 put)
    """

    strike: float
    maturity: float
    option_type: Literal["call", "put"] = "call"


@dataclass(frozen=True)
class SimulationSpec:
    """시뮬레이션 실행 설정값."""

    n_paths: int = 50_000
    n_steps: int = 252
    seed: int = 42


@dataclass(frozen=True)
class PricingResult:
    """가격 산출 결과.

    Attributes:
        price: 할인된 몬테카를로 추정 가격
        stdev: 할인된 페이오프 표준편차
        stderr: 표준오차
        ci_low: 95% 신뢰구간 하단
        ci_high: 95% 신뢰구간 상단
    """

    price: float
    stdev: float
    stderr: float
    ci_low: float
    ci_high: float


def _validate_inputs(market: MarketAssumption, contract: ContractSpec, sim: SimulationSpec) -> None:
    """입력값 유효성 검사를 수행해 계산 오류를 사전에 방지한다."""

    if market.spot <= 0:
        raise ValueError("spot은 0보다 커야 합니다.")
    if market.volatility < 0:
        raise ValueError("volatility는 음수가 될 수 없습니다.")
    if contract.strike <= 0:
        raise ValueError("strike는 0보다 커야 합니다.")
    if contract.maturity <= 0:
        raise ValueError("maturity는 0보다 커야 합니다.")
    if sim.n_paths < 1 or sim.n_steps < 1:
        raise ValueError("n_paths와 n_steps는 1 이상이어야 합니다.")


def simulate_terminal_prices(
    market: MarketAssumption,
    contract: ContractSpec,
    sim: SimulationSpec,
) -> np.ndarray:
    """GBM 가정 하에서 만기 시점의 기초자산 가격 분포를 시뮬레이션한다."""

    _validate_inputs(market, contract, sim)

    dt = contract.maturity / sim.n_steps
    drift = (market.rate - 0.5 * market.volatility**2) * dt
    diffusion_scale = market.volatility * sqrt(dt)

    rng = np.random.default_rng(sim.seed)
    shocks = rng.standard_normal(size=(sim.n_paths, sim.n_steps))

    log_returns = drift + diffusion_scale * shocks
    log_terminal = np.log(market.spot) + np.sum(log_returns, axis=1)

    return np.exp(log_terminal)


def _payoff(terminal_prices: np.ndarray, contract: ContractSpec) -> np.ndarray:
    """옵션 유형에 맞는 만기 페이오프를 계산한다."""

    if contract.option_type == "call":
        return np.maximum(terminal_prices - contract.strike, 0.0)
    if contract.option_type == "put":
        return np.maximum(contract.strike - terminal_prices, 0.0)
    raise ValueError("option_type은 'call' 또는 'put' 이어야 합니다.")


def price_option(
    market: MarketAssumption,
    contract: ContractSpec,
    sim: SimulationSpec,
) -> PricingResult:
    """몬테카를로 방식으로 유럽형 옵션 가격과 95% 신뢰구간을 산출한다."""

    terminal_prices = simulate_terminal_prices(market, contract, sim)
    payoff = _payoff(terminal_prices, contract)

    discount = exp(-market.rate * contract.maturity)
    discounted_payoff = discount * payoff

    price = float(np.mean(discounted_payoff))
    stdev = float(np.std(discounted_payoff, ddof=1))
    stderr = stdev / sqrt(sim.n_paths)
    ci_margin = 1.96 * stderr

    return PricingResult(
        price=price,
        stdev=stdev,
        stderr=stderr,
        ci_low=price - ci_margin,
        ci_high=price + ci_margin,
    )
