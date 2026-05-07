# Black-Scholes 옵션가격 계산 복습 노트

## 1. 복습 목표

이 문서는 유럽형 콜/풋 옵션의 Black-Scholes 가격이 어떤 논리와 계산 단계를 거쳐 나오는지 다시 확인하기 위한 노트다. 이 저장소의 기존 Monte Carlo 실험은 시뮬레이션 추정값을 Black-Scholes 해석해와 비교한다. 따라서 Black-Scholes 공식은 단순한 참고값이 아니라, GBM 가정 아래에서 “정답에 가까운 벤치마크” 역할을 한다.

연결 파일은 다음과 같다.

- 입력 시나리오: `data/sample/black_scholes_review_scenarios.csv`
- 계산 코드: `src/black_scholes.py`, `src/black_scholes_review.py`
- 실행 스크립트: `python -m src.run_black_scholes_review`
- 결과 테이블: `outputs/tables/black_scholes_review_results.csv`

## 2. 입력 변수와 단위

| 기호 | 코드 컬럼 | 의미 | 단위 |
|---|---|---|---|
| $S_0$ | `spot` | 현재 기초자산 가격 | 가격 단위 |
| $K$ | `strike` | 행사가격 | 가격 단위 |
| $T$ | `maturity` | 잔존만기 | 연 단위 |
| $r$ | `rate` | 연속복리 무위험 이자율 | 연율 |
| $\sigma$ | `volatility` | 기초자산 연율 변동성 | 연율 |
| option type | `option_type` | 콜 또는 풋 | `call`, `put` |

Black-Scholes 공식은 입력 변수가 모두 같은 시간 단위로 정렬되어 있다고 가정한다. 예를 들어 변동성이 연율이면 만기도 연 단위여야 하며, 이자율도 같은 연율 기준이어야 한다.

## 3. 위험중립 가격평가 직관

Black-Scholes 모형은 기초자산이 위험중립 세계에서 다음 GBM을 따른다고 둔다.

$$dS_t = r S_t dt + \sigma S_t dW_t$$

위험중립 세계에서는 기대수익률이 투자자의 주관적 기대수익률이 아니라 무위험 이자율 $r$로 바뀐다. 그래서 옵션 가격은 만기 payoff의 위험중립 기대값을 현재가로 할인한 값이다.

$$V_0 = e^{-rT}\mathbb{E}^{\mathbb{Q}}[\text{payoff}(S_T)]$$

Monte Carlo는 이 기대값을 난수 경로 평균으로 추정하고, Black-Scholes는 같은 기대값을 로그정규분포 적분으로 닫힌 형태로 계산한다.

## 4. d1과 d2

콜 옵션 공식은 다음과 같다.

$$C = S_0 N(d_1) - K e^{-rT} N(d_2)$$

$$d_1 = \frac{\ln(S_0/K) + (r + \sigma^2/2)T}{\sigma\sqrt{T}}, \quad d_2 = d_1 - \sigma\sqrt{T}$$

풋 옵션 공식은 다음과 같다.

$$P = K e^{-rT} N(-d_2) - S_0 N(-d_1)$$

해석할 때는 다음 순서가 유용하다.

1. $\ln(S_0/K)$는 현재 가격이 행사가보다 얼마나 위아래에 있는지 로그 기준으로 측정한다.
2. $\sigma\sqrt{T}$는 만기까지 누적되는 불확실성의 크기다.
3. $d_2$는 위험중립 분포에서 만기 행사 영역과 연결된다.
4. $d_1$은 기초자산 가격에 곱해지는 확률 가중치이며, 콜 Delta $N(d_1)$와 직접 연결된다.

## 5. 가격을 두 다리로 분해하기

콜 가격은 두 항의 차이다.

| 항 | 코드 컬럼 | 의미 |
|---|---|---|
| $S_0 N(d_1)$ | `stock_leg_value` | 행사될 때 받는 기초자산의 현재 가치 성격 |
| $K e^{-rT}N(d_2)$ | `bond_leg_value` | 행사될 때 지급하는 행사가의 현재 가치 성격 |

풋 가격도 같은 두 다리를 반대 방향으로 읽는다.

| 항 | 코드 컬럼 | 의미 |
|---|---|---|
| $K e^{-rT}N(-d_2)$ | `bond_leg_value` | 풋이 행사될 때 받는 행사가의 현재 가치 성격 |
| $S_0 N(-d_1)$ | `stock_leg_value` | 풋 payoff에서 차감되는 기초자산 가치 성격 |

따라서 결과 테이블에서 `stock_leg_value`, `bond_leg_value`, `price`를 함께 보면 공식이 단순 암기가 아니라 “받는 것에서 내는 것을 뺀 현재가”라는 구조로 보인다.

## 6. Greeks 복습 포인트

`src/black_scholes.py`는 가격과 함께 Delta, Gamma, Vega, Theta를 계산한다.

- Delta: 기초자산 가격이 1 단위 변할 때 옵션 가격의 1차 민감도.
- Gamma: Delta 자체가 얼마나 빨리 변하는지 나타내는 2차 민감도.
- Vega: 변동성이 1.00, 즉 100%p 변할 때 옵션 가격이 얼마나 변하는지 나타내는 민감도.
- Theta: 이 저장소에서는 1일 기준 시간가치 감소량으로 저장한다.

복습할 때는 ATM 옵션의 Gamma와 Vega가 상대적으로 크고, 깊은 ITM/OTM으로 갈수록 민감도 양상이 달라지는지 확인한다.

## 7. 검증 기준

Black-Scholes 계산은 다음 세 가지로 점검한다.

1. Put-Call Parity:

   $$C - P = S_0 - K e^{-rT}$$

   결과 테이블의 `put_call_parity_gap`이 0에 가까우면 콜/풋 계산이 같은 무차익 조건을 만족한다.

2. 입력 단위:

   만기, 이자율, 변동성의 시간 단위가 어긋나면 가격은 계산되더라도 의미가 없다.

3. 모형 한계:

   Black-Scholes는 상수 변동성, 연속 거래, 거래비용 없음, 배당 없음, 로그정규 기초자산 가격을 가정한다. 실제 시장의 변동성 스마일, 점프, 유동성 비용은 별도 모형이나 보정이 필요하다.

## 8. 실행 방법

```bash
python -m src.run_black_scholes_review
```

실행 후 `outputs/tables/black_scholes_review_results.csv`에서 다음 순서로 확인한다.

1. `d1`, `d2`가 moneyness와 volatility 변화에 따라 어떻게 움직이는지 본다.
2. `stock_leg_value`, `bond_leg_value` 중 어느 항이 가격을 주도하는지 본다.
3. `delta`, `vega`, `theta_per_day`를 통해 가격 민감도의 방향을 본다.
4. `put_call_parity_gap`이 0에 가까운지 확인해 계산 일관성을 점검한다.
