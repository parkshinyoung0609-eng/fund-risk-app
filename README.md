# 펀드 리스크 의사결정 지원 시스템

펀드 성과 데이터를 분석하여 리스크를 감지하고, 관련 판례·금융위 결정문과 연결해주는 투자심사 보조 도구입니다.

---

## 시스템 구성

```
screening_project/
├── backend/          # Python FastAPI
├── frontend/         # React + TypeScript + Vite
└── data/             # 샘플 CSV 및 데이터 생성 스크립트
```

---

## 빠른 시작

### 1. PostgreSQL 준비

```bash
createdb fund_risk_db
```

### 2. 백엔드 실행

```bash
cd backend
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에서 DATABASE_URL 수정

cd ..
PYTHONPATH=backend uvicorn app.main:app --reload --app-dir backend
```

> **MOCK_EXTERNAL_APIS=true** 로 설정하면 법원 API / 금융위 API 없이도 mock 데이터로 동작합니다.

API 문서: http://localhost:8000/docs

### 3. 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

브라우저: http://localhost:5173

---

## 사용 방법

### Step 1 – CSV 업로드

대시보드 상단의 CSV 업로드 패널에서 두 파일을 업로드합니다.

| 파일 | 설명 |
|---|---|
| `data/sample_fund_master.csv` | 펀드 기본정보 |
| `data/sample_fund_price_history.csv` | 일별 NAV 이력 (252일) |

### Step 2 – 전체 분석 실행

펀드 상세 페이지에서 **[전체 분석 실행]** 버튼을 누릅니다.

내부적으로 4단계를 순차 실행합니다.

```
1. 지표 계산   → 누적수익률, 연환산변동성, 샤프지수, MDD 등
2. 리스크 감지 → 룰 기반으로 HIGH_VOLATILITY, LARGE_DRAWDOWN 등 감지
3. 사례 검색   → 리스크 코드별 관련 판례·결정문 매칭
4. 리포트 생성 → 종합 등급(안전/보통/주의/위험) 및 체크리스트 생성
```

### Step 3 – 리포트 확인

펀드 상세 페이지에서 **[리포트 보기]** 버튼으로 투자심사 지원 리포트를 확인합니다.

---

## 리스크 룰

| 코드 | 조건 | 심각도 |
|---|---|---|
| HIGH_VOLATILITY | 연환산 변동성 > 25% | 높음 |
| LOW_SHARPE | 샤프지수 < 0.3 | 중간 |
| LARGE_DRAWDOWN | MDD < -20% | 높음 |
| SHORT_TERM_DROP | 최근 1개월 수익률 < -10% | 높음 |
| UNDERPERFORM_BM | 최근 6개월 벤치마크 대비 부진 | 중간 |
| HIGH_FEE_LOW_RETURN | 보수 ≥ 1% & 연환산수익 < 5% | 중간 |
| LEGAL_REVIEW_REQUIRED | 위 리스크 2개 이상 동시 발생 | 높음 |

---

## 등급 산정

| 점수 | 등급 |
|---|---|
| 85점 이상 | 안전 |
| 70~84점 | 보통 |
| 50~69점 | 주의 |
| 50점 미만 | 위험 |

---

## 외부 API 연동

| API | 용도 | Mock 지원 |
|---|---|---|
| law.go.kr 판례 목록/본문 | 관련 판례 검색 | ✅ |
| 공공데이터포털 증권 분쟁 결정문 | 금융위 결정문 검색 | ✅ |

실제 API 키는 `.env`의 `LAW_API_KEY`, `SFC_API_KEY`에 설정합니다.
`MOCK_EXTERNAL_APIS=false`로 변경하면 실제 API를 호출합니다.

---

## 주의 문구

본 시스템은 **투자심사 보조자료**이며, 최종 투자 여부는 담당자의 종합 판단과 내부 심사 절차에 따라 결정되어야 합니다.
