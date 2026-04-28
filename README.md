# Monte Carlo Pricing Simulation

GBM 가정 하에서 파생상품 공정가치를 Monte Carlo 방식으로 추정하는 포트폴리오형 연구 저장소.

**핵심 연구 질문**

> 설정 가능한 시장 가정 아래에서 Monte Carlo 시뮬레이션은 파생상품 가격을 얼마나 안정적으로 추정할 수 있으며, 그 결과로부터 어떤 실무적 통찰을 얻을 수 있는가?

---

## 작업 기준 문서

- `AGENTS.md`: 저장소 작업 기준과 품질 기준
- `SOURCE.md`: KAIST-DFMBA 참고 경로와 프로젝트별 컨텐츠 재구성 기준

## 저장소 구조

```
option-pricing/
├── src/
│   ├── monte_carlo_engine.py   # GBM terminal price, European MC pricing, CI
│   ├── black_scholes.py        # BS 해석해, Greeks, Put-Call Parity 검증
│   ├── gbm_paths.py            # 전체 경로 배열 생성 (시각화·경로의존형 옵션용)
│   ├── asian_option.py         # Arithmetic/Geometric Asian option MC + 해석해
│   ├── convergence.py          # 경로 수별 수렴 분석
│   └── config.py               # 경로 설정
├── notebooks/
│   ├── 01_gbm_path_simulation.ipynb       # GBM 경로 시각화, 분포 검증
│   ├── 02_european_option_mc_vs_bs.ipynb  # MC vs BS 벤치마크, 오차 분석
│   ├── 03_convergence_analysis.ipynb      # 수렴 속도, CI 폭, 목표 정밀도
│   └── 04_asian_option_pricing.ipynb      # Asian option, European 비교
├── data/
│   └── sample/option_scenarios.csv        # 재현 가능한 데모 시나리오
├── outputs/
│   ├── charts/                            # 생성된 차트 (PNG)
│   └── tables/                            # 생성된 결과 테이블 (CSV)
├── docs/
│   └── methodology.md                     # GBM, BS, Asian, 수렴 분석 수식 정리
└── requirements.txt
```

---

## 구현 범위

| 모듈 | 기능 |
|---|---|
| `monte_carlo_engine` | GBM 만기 가격 시뮬레이션, 유럽형 콜/풋 MC 가격, 95% CI |
| `black_scholes` | BS 해석해(콜/풋), Delta/Gamma/Vega/Theta, Put-Call Parity 검증 |
| `gbm_paths` | 전체 경로 배열 `(n_paths, n_steps+1)` 생성 |
| `asian_option` | Arithmetic/Geometric Asian MC, Geometric 해석해(Kemna & Vorst) |
| `convergence` | 경로 수 격자별 수렴 테이블, 이론 O(1/sqrt(N)) 기준선 |

---

## 빠른 시작

```bash
pip install -r requirements.txt
```

**시나리오 실험 실행**

```bash
python -m src.run_pricing_experiment
# → outputs/tables/pricing_results_sample.csv
# → outputs/charts/pricing_results_sample.png
```

**노트북 실행**

```bash
jupyter notebook notebooks/
```

**단일 가격 산출 예시**

```python
from src import MarketAssumption, ContractSpec, SimulationSpec, price_option, bs_price

market   = MarketAssumption(spot=100.0, rate=0.03, volatility=0.20)
contract = ContractSpec(strike=100.0, maturity=1.0, option_type='call')
sim      = SimulationSpec(n_paths=50_000, n_steps=252, seed=42)

mc = price_option(market, contract, sim)
bs = bs_price(market, contract)

print(f'MC: {mc.price:.4f}  CI=[{mc.ci_low:.4f}, {mc.ci_high:.4f}]')
print(f'BS: {bs.price:.4f}  delta={bs.delta:.4f}')
```

---

## 분석 노트북 요약

### 01. GBM 경로 시뮬레이션
- 샘플 경로 50개 시각화
- 만기 가격 분포 → 로그정규 분포 검증
- 변동성 수준(σ = 0.10 ~ 0.50)별 경로 분산 비교

### 02. 유럽형 옵션: MC vs Black-Scholes
- 기준 시나리오에서 MC vs BS 가격 비교 (50,000 경로 기준 상대 오차 < 0.5%)
- 변동성 격자(σ = 0.05 ~ 0.60)에서 오차 분석
- Put-Call Parity 수치 검증
- 행사가격별 가격 곡선 비교

### 03. 수렴 분석 및 신뢰구간
- 경로 수 100 ~ 100,000 구간에서 수렴 확인
- CI 폭 vs 이론 O(1/sqrt(N)) 곡선 비교
- 목표 정밀도별 필요 경로 수 역산
- 30개 시드에서 안정성 확인

### 04. Asian Option 가격 산출
- Arithmetic vs Geometric Asian vs European 가격 비교
- Geometric Asian MC vs Kemna & Vorst 해석해 검증
- 변동성·만기별 Asian/European 가격 비율 분석
- 경로별 평균 가격 vs 만기 가격 시각화

---

## 주요 결과 (기준 시나리오: S=100, K=100, T=1, r=3%, σ=20%)

| 모델 | 가격 |
|---|---|
| Black-Scholes (해석해) | 9.4134 |
| European MC (50,000 경로) | ≈ 9.41 ± 0.04 |
| Asian Arithmetic MC | ≈ 5.34 |
| Asian Geometric MC | ≈ 5.15 |
| Asian Geometric BS | ≈ 5.06 |

MC 표준오차는 경로 수 N에 대해 O(1/sqrt(N))으로 감소한다.

---

## 방법론

→ [`docs/methodology.md`](docs/methodology.md) 참조

GBM 이산화, BS 공식, Asian option 해석해(Kemna & Vorst), 수렴 진단 수식을 정리했다.

---

## 확장 방향

- 분산 축소 기법 (Antithetic Variates, Control Variates)
- Greeks 수치 근사 (Finite Difference)
- 변동성 스마일 / 국소 변동성 모형
- VaR / Expected Shortfall 시나리오 엔진
- Barrier option, Lookback option 등 이색옵션 확장
