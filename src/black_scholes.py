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


def _validate_bs_inputs(market: MarketAssumption, contract: ContractSpec) -> None:
    """Black-Scholes 공식에 들어가는 입력값을 검증한다.

    MC 엔진의 입력 검증과 같은 원칙을 사용하지만, BS 공식은 시뮬레이션 설정이 없으므로
    시장 가정과 계약 조건만 별도로 확인한다. 로그, 제곱근, 확률분포 함수에 들어가는 값이
    경제적으로도 수학적으로도 가능한 범위인지 확인하는 단계다.
    """
    if market.spot <= 0:
        raise ValueError("spot은 0보다 커야 합니다.")
    if market.volatility < 0:
        raise ValueError("volatility는 음수가 될 수 없습니다.")
    if contract.strike <= 0:
        raise ValueError("strike는 0보다 커야 합니다.")
    if contract.maturity <= 0:
        raise ValueError("maturity는 0보다 커야 합니다.")
    if contract.option_type not in {"call", "put"}:
        raise ValueError("option_type은 'call' 또는 'put' 이어야 합니다.")


def bs_price(market: MarketAssumption, contract: ContractSpec) -> BSResult:
    """Black-Scholes 공식으로 유럽형 옵션 가격과 Greeks를 계산한다.

    변동성이 0이면 위험중립 확정 만기 가격으로 payoff를 계산한 뒤 현재가로 할인한다.
    """
    _validate_bs_inputs(market, contract)

    S = market.spot
    K = contract.strike
    r = market.rate
    sigma = market.volatility
    T = contract.maturity
    opt = contract.option_type

    # 변동성이 0이면 확률분포가 퇴화하므로 d1/d2가 정의되지 않는다.
    # 이 경우에는 위험중립 세계의 확정 만기 가격 S_T = S0 * exp(rT)를 직접 payoff에 넣고 할인한다.
    # 단순 현재 내재가치 max(S0-K, 0)를 할인하면 이자율 효과를 빠뜨리므로 주의한다.
    if sigma == 0.0:
        deterministic_terminal = S * exp(r * T)
        payoff = (
            max(deterministic_terminal - K, 0.0)
            if opt == "call"
            else max(K - deterministic_terminal, 0.0)
        )
        delta = float(deterministic_terminal > K) if opt == "call" else -float(deterministic_terminal < K)
        return BSResult(price=payoff * exp(-r * T), delta=delta, gamma=0.0, vega=0.0, theta=0.0)

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
