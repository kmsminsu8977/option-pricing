## 0. 기준 문서

- `AGENTS.md`: 작업 기준과 품질 기준
- `SOURCE.md`: 참고 경로와 컨텐츠 재구성 기준

# 방법론 노트

## 1. 기하 브라운 운동 (GBM)

기초자산 가격 $S_t$가 다음 확률미분방정식을 따른다고 가정한다.

$$dS_t = r S_t \, dt + \sigma S_t \, dW_t$$

여기서 $r$은 무위험 이자율, $\sigma$는 연율 변동성, $W_t$는 표준 브라운 운동이다.

이토 보조정리(Itô's Lemma)를 적용하면 해석해는 다음과 같다.

$$S_t = S_0 \exp\!\left[\left(r - \tfrac{1}{2}\sigma^2\right)t + \sigma W_t\right]$$

이산화 시뮬레이션에서는 시간 간격 $\Delta t = T/n$ 으로 분할해 다음을 반복한다.

$$S_{t+\Delta t} = S_t \exp\!\left[\left(r - \tfrac{1}{2}\sigma^2\right)\Delta t + \sigma\sqrt{\Delta t}\, Z_t\right], \quad Z_t \sim \mathcal{N}(0,1)$$

## 2. 유럽형 옵션 MC 가격 산출

$N$개의 경로를 시뮬레이션해 만기 페이오프의 기대값을 추정한다.

$$\hat{C} = e^{-rT} \frac{1}{N} \sum_{i=1}^{N} \max(S_T^{(i)} - K,\, 0)$$

중심극한정리에 의해 $\hat{C}$는 점근적으로 정규분포를 따르며, 95% 신뢰구간은 다음과 같다.

$$\hat{C} \pm 1.96 \cdot \frac{\hat{\sigma}}{\sqrt{N}}$$

표준오차는 $O(1/\sqrt{N})$으로 감소한다. 정밀도를 2배 높이려면 경로 수를 4배 늘려야 한다.

## 3. Black-Scholes 해석해

GBM 가정 하에서 유럽형 콜 옵션의 무차익 가격은 다음과 같다.

$$C = S_0 N(d_1) - K e^{-rT} N(d_2)$$

$$d_1 = \frac{\ln(S_0/K) + (r + \sigma^2/2)T}{\sigma\sqrt{T}}, \quad d_2 = d_1 - \sigma\sqrt{T}$$

풋 옵션은 Put-Call Parity로 도출한다.

$$P = C - S_0 + K e^{-rT}$$

이 저장소에서 BS 가격은 MC 결과의 벤치마크로 사용된다.

## 4. Asian Option

경로 평균 가격을 페이오프 기준으로 사용하는 경로의존형 옵션이다.

**산술평균 Asian Call**

$$C_{\text{Asian}} = e^{-rT} \mathbb{E}\!\left[\max\!\left(\bar{S}_{\text{arith}} - K,\, 0\right)\right], \quad \bar{S}_{\text{arith}} = \frac{1}{n}\sum_{i=1}^{n} S_{t_i}$$

해석해가 없어 MC가 필수적이다.

**기하평균 Asian Call (Kemna & Vorst, 1990)**

$$\bar{S}_{\text{geo}} = \exp\!\left(\frac{1}{n}\sum_{i=1}^{n} \ln S_{t_i}\right)$$

이산 모니터링 조정 파라미터를 사용한 해석해가 존재하며, MC 기하평균 결과의 검증 기준으로 활용한다.

$$\sigma^* = \sigma\sqrt{\frac{2n+1}{6(n+1)}}, \quad r^* = \frac{1}{2}\!\left(r - \frac{\sigma^2}{2} + {\sigma^*}^2\right)$$

## 5. 수렴 진단

경로 수 $N$에 따른 MC 추정의 안정성을 다음 지표로 평가한다.

- **표준오차**: $\text{SE} = \hat{\sigma}/\sqrt{N}$
- **95% CI 폭**: $2 \times 1.96 \times \text{SE}$
- **이론 수렴 곡선**: $O(1/\sqrt{N})$ 기준선과 실제 수렴 속도 비교

목표 CI 폭 $w$를 달성하기 위한 최소 경로 수는 다음과 같다.

$$N^* = \left\lceil \left(\frac{2 \times 1.96 \times \hat{\sigma}}{w}\right)^2 \right\rceil$$

## 참고 문헌

- Black, F., & Scholes, M. (1973). The pricing of options and corporate liabilities. *Journal of Political Economy*, 81(3), 637–654.
- Kemna, A. G. Z., & Vorst, A. C. F. (1990). A pricing method for options based on average asset values. *Journal of Banking & Finance*, 14(1), 113–129.
- Glasserman, P. (2003). *Monte Carlo Methods in Financial Engineering*. Springer.
