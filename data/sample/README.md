# 샘플 데이터 안내

이 디렉터리는 몬테카를로 가격 산출 실험을 재현하기 위한 최소 입력값을 제공합니다.

## 파일 설명

- `option_scenarios.csv`
  - 시나리오 기반 옵션 가격 실험 입력 테이블
  - 각 행은 하나의 가격 산출 실험 단위를 의미
- `black_scholes_review_scenarios.csv`
  - Black-Scholes 공식 복습용 합성 시나리오
  - Monte Carlo 경로 수 없이 `d1`, `d2`, 할인계수, 가격 분해항, Greeks를 확인하기 위한 입력값

## 컬럼 정의

### `option_scenarios.csv`

- `scenario_id`: 시나리오 식별자
- `option_type`: `call` 또는 `put`
- `spot`: 현재 기초자산 가격
- `strike`: 행사가격
- `maturity`: 잔존만기(년)
- `rate`: 무위험 이자율(연율)
- `volatility`: 연율 변동성
- `n_paths`: 몬테카를로 경로 수
- `n_steps`: 만기까지의 시간 분할 수
- `seed`: 난수 시드

### `black_scholes_review_scenarios.csv`

- `scenario_id`: 복습 시나리오 식별자
- `lesson_focus`: 해당 행에서 관찰할 공식 해석 포인트
- `option_type`: `call` 또는 `put`
- `spot`: 현재 기초자산 가격 `S0`
- `strike`: 행사가격 `K`
- `maturity`: 잔존만기 `T`(연 단위)
- `rate`: 연속복리 무위험 이자율 `r`
- `volatility`: 연율 변동성 `sigma`

## 사용 방법

아래 명령으로 시나리오를 실행하면 `outputs/tables/`, `outputs/charts/`에 결과가 저장됩니다.

```bash
python -m src.run_pricing_experiment
```

Black-Scholes 공식의 중간 계산값을 복습하려면 아래 명령을 실행합니다.

```bash
python -m src.run_black_scholes_review
```
