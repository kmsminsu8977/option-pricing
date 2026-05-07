"""Black-Scholes 공식 복습용 계산 분해 모듈.

`src.black_scholes`가 최종 가격과 Greeks를 빠르게 반환하는 생산용 함수라면,
이 모듈은 학습자가 공식의 각 항을 눈으로 따라갈 수 있도록 중간 계산값을 표 형태로 펼친다.

핵심 관점:
- d1은 기초자산 가격에 곱해지는 확률 가중치와 Delta를 이해하는 관문이다.
- d2는 위험중립 세계에서 만기 행사 여부를 해석할 때 자주 쓰인다.
- 콜 가격은 `기초자산항 - 할인 행사가항`, 풋 가격은 `할인 행사가항 - 기초자산항`으로 분해된다.
- Put-Call Parity 잔차를 함께 기록해 계산 결과가 무차익 관계와 일관적인지 확인한다.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import exp, log, sqrt

import pandas as pd
from scipy.stats import norm

from src.black_scholes import bs_price
from src.monte_carlo_engine import ContractSpec, MarketAssumption


@dataclass(frozen=True)
class BlackScholesStepResult:
    """Black-Scholes 공식의 중간 계산값을 한 행으로 담는 복습용 결과.

    각 필드는 `outputs/tables/black_scholes_review_results.csv`의 컬럼으로 저장된다.
    가격만 보면 공식이 암기 대상처럼 보이기 쉬우므로, 이 결과 객체는 d1/d2, 할인계수,
    확률 가중치, 가격 분해항, Greeks, parity 검증값을 같은 행에 묶는다.
    """

    scenario_id: str
    lesson_focus: str
    option_type: str
    spot: float
    strike: float
    maturity: float
    rate: float
    volatility: float
    forward_price: float
    discount_factor: float
    log_moneyness: float
    sigma_sqrt_time: float
    d1: float
    d2: float
    stock_leg_probability: float
    bond_leg_probability: float
    stock_leg_value: float
    bond_leg_value: float
    price: float
    delta: float
    gamma: float
    vega: float
    theta_per_day: float
    put_call_parity_gap: float

    def to_dict(self) -> dict[str, float | str]:
        """CSV 저장과 pandas 변환에 사용할 수 있는 평평한 dict로 변환한다."""
        return asdict(self)


def _validate_review_inputs(market: MarketAssumption, contract: ContractSpec) -> None:
    """d1/d2 분해가 가능한 입력인지 확인한다.

    BS 가격 자체는 변동성이 0인 극한 사례도 처리할 수 있지만, 이 복습 테이블은
    `sigma * sqrt(T)`로 표준화하는 d1/d2를 직접 보여주는 목적이므로 양의 변동성을 요구한다.
    """
    if market.spot <= 0:
        raise ValueError("spot은 0보다 커야 합니다.")
    if contract.strike <= 0:
        raise ValueError("strike는 0보다 커야 합니다.")
    if contract.maturity <= 0:
        raise ValueError("maturity는 0보다 커야 합니다.")
    if market.volatility <= 0:
        raise ValueError("복습용 d1/d2 분해에서는 volatility가 0보다 커야 합니다.")
    if contract.option_type not in {"call", "put"}:
        raise ValueError("option_type은 'call' 또는 'put' 이어야 합니다.")


def explain_black_scholes_price(
    market: MarketAssumption,
    contract: ContractSpec,
    scenario_id: str,
    lesson_focus: str = "",
) -> BlackScholesStepResult:
    """단일 옵션 계약의 Black-Scholes 계산 과정을 단계별 결과로 반환한다.

    Args:
        market: 현재 가격, 무위험 이자율, 변동성으로 구성된 시장 가정.
        contract: 행사가, 만기, 콜/풋 유형으로 구성된 유럽형 옵션 계약 조건.
        scenario_id: 복습 테이블에서 시나리오를 식별하기 위한 이름.
        lesson_focus: 해당 행에서 관찰할 학습 포인트. 예: ATM, 고변동성, 단기만기.

    Returns:
        Black-Scholes 공식의 중간 항과 최종 가격, Greeks, parity 잔차를 포함한 결과 객체.
    """
    _validate_review_inputs(market, contract)

    S = market.spot
    K = contract.strike
    r = market.rate
    sigma = market.volatility
    T = contract.maturity
    opt = contract.option_type

    # 선도 가격과 할인계수는 BS 공식을 무차익 가격평가 관점에서 읽기 위한 기본 재료다.
    # forward_price가 strike보다 높으면 위험중립 평균 기준으로 콜이 유리한 영역에 가까워진다.
    discount_factor = exp(-r * T)
    forward_price = S / discount_factor

    # log_moneyness는 단순 S/K보다 수식에 직접 들어가는 형태다.
    # sigma_sqrt_time은 만기까지 누적되는 불확실성의 크기이며 d1과 d2의 분모로 쓰인다.
    log_moneyness = log(S / K)
    sigma_sqrt_time = sigma * sqrt(T)
    d1 = (log_moneyness + (r + 0.5 * sigma**2) * T) / sigma_sqrt_time
    d2 = d1 - sigma_sqrt_time

    # 콜과 풋은 같은 d1/d2를 쓰지만 누적정규분포를 적용하는 방향이 반대다.
    # stock_leg_probability는 S0에 곱해지는 확률 가중치, bond_leg_probability는 할인 행사가에 곱해지는
    # 확률 가중치로 해석하면 가격 공식의 두 다리를 분리해서 볼 수 있다.
    if opt == "call":
        stock_leg_probability = float(norm.cdf(d1))
        bond_leg_probability = float(norm.cdf(d2))
        stock_leg_value = S * stock_leg_probability
        bond_leg_value = K * discount_factor * bond_leg_probability
        decomposed_price = stock_leg_value - bond_leg_value
    else:
        stock_leg_probability = float(norm.cdf(-d1))
        bond_leg_probability = float(norm.cdf(-d2))
        stock_leg_value = S * stock_leg_probability
        bond_leg_value = K * discount_factor * bond_leg_probability
        decomposed_price = bond_leg_value - stock_leg_value

    bs_result = bs_price(market, contract)

    # Put-Call Parity는 같은 S, K, T, r에서 콜과 풋 가격이 동시에 만족해야 하는 무차익 관계다.
    # 현재 행이 콜이면 대응 풋을, 풋이면 대응 콜을 계산해 C - P - (S - K*DF)가 0에 가까운지 기록한다.
    opposite_type = "put" if opt == "call" else "call"
    opposite_contract = ContractSpec(strike=K, maturity=T, option_type=opposite_type)
    opposite_price = bs_price(market, opposite_contract).price
    parity_left = decomposed_price - opposite_price if opt == "call" else opposite_price - decomposed_price
    parity_right = S - K * discount_factor
    put_call_parity_gap = parity_left - parity_right

    return BlackScholesStepResult(
        scenario_id=scenario_id,
        lesson_focus=lesson_focus,
        option_type=opt,
        spot=S,
        strike=K,
        maturity=T,
        rate=r,
        volatility=sigma,
        forward_price=forward_price,
        discount_factor=discount_factor,
        log_moneyness=log_moneyness,
        sigma_sqrt_time=sigma_sqrt_time,
        d1=d1,
        d2=d2,
        stock_leg_probability=stock_leg_probability,
        bond_leg_probability=bond_leg_probability,
        stock_leg_value=stock_leg_value,
        bond_leg_value=bond_leg_value,
        # 가격은 생산용 bs_price와 같은 값을 사용해 공개 API와 복습 테이블이 같은 기준을 공유하게 한다.
        price=bs_result.price,
        delta=bs_result.delta,
        gamma=bs_result.gamma,
        vega=bs_result.vega,
        theta_per_day=bs_result.theta,
        put_call_parity_gap=put_call_parity_gap,
    )


def build_black_scholes_review_table(scenarios: pd.DataFrame) -> pd.DataFrame:
    """샘플 시나리오 DataFrame을 Black-Scholes 복습용 결과 테이블로 변환한다.

    입력 CSV는 투자 성과를 주장하기 위한 실제 시장 데이터가 아니라, 공식의 민감도를
    복습하기 위한 합성 예제다. 따라서 각 행의 `lesson_focus`를 함께 남겨 사용자가
    가격 변화의 원인을 다시 추적할 수 있게 한다.
    """
    required_columns = {
        "scenario_id",
        "lesson_focus",
        "option_type",
        "spot",
        "strike",
        "maturity",
        "rate",
        "volatility",
    }
    missing = required_columns - set(scenarios.columns)
    if missing:
        raise ValueError(f"필수 컬럼이 없습니다: {sorted(missing)}")

    results: list[BlackScholesStepResult] = []
    for _, row in scenarios.iterrows():
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
        results.append(
            explain_black_scholes_price(
                market=market,
                contract=contract,
                scenario_id=str(row["scenario_id"]),
                lesson_focus=str(row["lesson_focus"]),
            )
        )

    return pd.DataFrame([result.to_dict() for result in results])
