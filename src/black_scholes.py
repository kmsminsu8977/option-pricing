"""Black-Scholes 해석해 모듈.

유럽형 콜/풋 옵션의 BS 가격과 주요 Greeks를 계산한다.
MC 결과의 벤치마크 및 오차 분석에 사용된다.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, log, sqrt

from scipy.stats import norm

from src.monte_carlo_engine import ContractSpec, MarketAssumption


@dataclass(frozen=True)
class BSResult:
    """Black-Scholes 가격 산출 결과."""

    price: float
    delta: float
    gamma: float
    vega: float
    theta: float


def _d1_d2(market: MarketAssumption, contract: ContractSpec) -> tuple[float, float]:
    """d1, d2 보조 변수를 계산한다."""
    # 기호를 수식 표기와 맞춰 짧은 변수명으로 변환하면 공식 대응 관계가 명확해진다.
    S = market.spot
    K = contract.strike
    r = market.rate
    sigma = market.volatility
    T = contract.maturity

    d1 = (log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    return d1, d2


def bs_price(market: MarketAssumption, contract: ContractSpec) -> BSResult:
    """Black-Scholes 공식으로 유럽형 옵션 가격과 Greeks를 계산한다.

    변동성이 0이면 내재가치(intrinsic value)를 반환한다.
    """
    S = market.spot
    K = contract.strike
    r = market.rate
    sigma = market.volatility
    T = contract.maturity
    opt = contract.option_type

    # 변동성이 0이면 확률분포가 퇴화하므로 Black-Scholes d1/d2 대신 할인 내재가치를 반환한다.
    if sigma == 0.0:
        intrinsic = max(S - K, 0.0) if opt == "call" else max(K - S, 0.0)
        return BSResult(price=intrinsic * exp(-r * T), delta=float(S > K), gamma=0.0, vega=0.0, theta=0.0)

    d1, d2 = _d1_d2(market, contract)
    disc = exp(-r * T)

    # 콜/풋 가격과 Delta는 payoff 방향이 달라 분기하고, Gamma/Vega는 같은 공식을 공유한다.
    if opt == "call":
        price = S * norm.cdf(d1) - K * disc * norm.cdf(d2)
        delta = float(norm.cdf(d1))
    else:
        price = K * disc * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = float(norm.cdf(d1) - 1.0)

    gamma = float(norm.pdf(d1) / (S * sigma * sqrt(T)))
    vega = float(S * norm.pdf(d1) * sqrt(T))

    # theta: 1일 기준 시간가치 감소
    if opt == "call":
        theta = float(
            (-S * norm.pdf(d1) * sigma / (2 * sqrt(T)) - r * K * disc * norm.cdf(d2)) / 365
        )
    else:
        theta = float(
            (-S * norm.pdf(d1) * sigma / (2 * sqrt(T)) + r * K * disc * norm.cdf(-d2)) / 365
        )

    return BSResult(price=price, delta=delta, gamma=gamma, vega=vega, theta=theta)


def bs_put_call_parity_check(
    market: MarketAssumption,
    maturity: float,
    strike: float,
) -> dict[str, float]:
    """Put-Call Parity 성립 여부를 수치로 확인한다.

    C - P = S - K * exp(-rT) 가 성립해야 한다.
    """
    call_spec = ContractSpec(strike=strike, maturity=maturity, option_type="call")
    put_spec = ContractSpec(strike=strike, maturity=maturity, option_type="put")

    call_price = bs_price(market, call_spec).price
    put_price = bs_price(market, put_spec).price

    # 좌변은 실제 계산한 콜-풋 가격 차이, 우변은 무차익 parity 이론값이다.
    lhs = call_price - put_price
    rhs = market.spot - strike * exp(-market.rate * maturity)
    error = abs(lhs - rhs)

    return {"call": call_price, "put": put_price, "lhs": lhs, "rhs": rhs, "parity_error": error}
