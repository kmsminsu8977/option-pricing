"""Monte Carlo pricing simulation package.

이 패키지는 노트북과 실행 스크립트에서 자주 쓰는 핵심 객체와 함수를 한 번에 가져올 수 있도록
공개 API를 정리한다. 계산 로직은 각 모듈에 남겨두고, 이 파일은 사용 편의성을 위한 재수출 역할만 한다.
"""

# 시장 가정, 계약 조건, 시뮬레이션 설정, 유럽형 옵션 MC pricing 함수를 최상위 API로 노출한다.
from src.monte_carlo_engine import (
    MarketAssumption,
    ContractSpec,
    SimulationSpec,
    PricingResult,
    simulate_terminal_prices,
    price_option,
)
# Black-Scholes 해석해와 parity 검증 함수는 MC 결과의 benchmark로 사용한다.
from src.black_scholes import BSResult, bs_price, bs_put_call_parity_check
# 전체 경로 생성 함수는 시각화와 경로의존형 옵션 계산에서 사용한다.
from src.gbm_paths import simulate_paths, time_grid
# Asian option 관련 함수는 평균가격형 payoff 실험을 위해 별도 모듈에서 가져온다.
from src.asian_option import AsianSpec, price_asian_option, geometric_asian_analytical
# 수렴 분석 함수는 경로 수 변화에 따른 표준오차와 신뢰구간 폭을 점검한다.
from src.convergence import run_convergence_analysis, theoretical_stderr

# __all__은 `from src import *` 사용 시 공개할 이름을 명시해 내부 구현이 무분별하게 노출되는 것을 막는다.
__all__ = [
    "MarketAssumption",
    "ContractSpec",
    "SimulationSpec",
    "PricingResult",
    "simulate_terminal_prices",
    "price_option",
    "BSResult",
    "bs_price",
    "bs_put_call_parity_check",
    "simulate_paths",
    "time_grid",
    "AsianSpec",
    "price_asian_option",
    "geometric_asian_analytical",
    "run_convergence_analysis",
    "theoretical_stderr",
]
