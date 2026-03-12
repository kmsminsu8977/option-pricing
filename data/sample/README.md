# 샘플 데이터 안내

이 디렉터리는 몬테카를로 가격 산출 실험을 재현하기 위한 최소 입력값을 제공합니다.

## 파일 설명

- `option_scenarios.csv`
  - 시나리오 기반 옵션 가격 실험 입력 테이블
  - 각 행은 하나의 가격 산출 실험 단위를 의미

## 컬럼 정의

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

## 사용 방법

아래 명령으로 시나리오를 실행하면 `outputs/tables/`, `outputs/charts/`에 결과가 저장됩니다.

```bash
python -m src.run_pricing_experiment
```
