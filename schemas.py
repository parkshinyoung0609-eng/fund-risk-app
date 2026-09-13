from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class FundBase(BaseModel):
    fund_code: str
    fund_name: str
    manager: Optional[str] = None
    fund_type: Optional[str] = None
    launch_date: Optional[date] = None
    total_asset: Optional[Decimal] = None
    fee: Optional[Decimal] = None
    description: Optional[str] = None


class FundResponse(FundBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class FundPriceResponse(BaseModel):
    id: int
    fund_id: int
    price_date: date
    nav: Decimal
    benchmark_nav: Optional[Decimal] = None

    model_config = {"from_attributes": True}


class FundMetricResponse(BaseModel):
    id: int
    fund_id: int
    period: Optional[str] = None

    # 수익률
    cumulative_return: Optional[Decimal] = None
    annual_return: Optional[Decimal] = None
    benchmark_return: Optional[Decimal] = None
    excess_return: Optional[Decimal] = None

    # KFR 위험지표 (주간수익률 기반)
    annual_volatility: Optional[Decimal] = None       # 표준편차
    downside_risk: Optional[Decimal] = None           # 하락위험도
    r_squared: Optional[Decimal] = None               # 결정계수
    beta: Optional[Decimal] = None                    # 회귀식베타
    tracking_error: Optional[Decimal] = None          # 트레킹에러

    # KFR 위험조정지표
    sharpe_ratio: Optional[Decimal] = None            # 샤프지수
    modified_sharpe_ratio: Optional[Decimal] = None   # 수정샤프지수
    coefficient_of_variation: Optional[Decimal] = None  # 변동계수
    treynor_ratio: Optional[Decimal] = None           # 트레이너지수
    jensen_alpha: Optional[Decimal] = None            # 젠센알파
    information_ratio: Optional[Decimal] = None       # 정보비율(IR)
    max_drawdown: Optional[Decimal] = None            # MDD
    winning_ratio: Optional[Decimal] = None           # 승률

    calculated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RiskAlertResponse(BaseModel):
    id: int
    fund_id: int
    risk_code: Optional[str] = None
    severity: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    detected_value: Optional[Decimal] = None
    threshold_value: Optional[Decimal] = None
    detected_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LegalCaseResponse(BaseModel):
    id: int
    source: str
    case_id: Optional[str] = None
    case_name: Optional[str] = None
    case_number: Optional[str] = None
    decision_date: Optional[date] = None
    organization: Optional[str] = None
    summary: Optional[str] = None
    full_text: Optional[str] = None
    source_url: Optional[str] = None
    keywords: Optional[List[str]] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RiskCaseMatchResponse(BaseModel):
    id: int
    risk_alert_id: int
    legal_case_id: int
    match_keyword: Optional[str] = None
    similarity_score: Optional[Decimal] = None
    reason: Optional[str] = None
    legal_case: Optional[LegalCaseResponse] = None

    model_config = {"from_attributes": True}


class ReviewReportResponse(BaseModel):
    id: int
    fund_id: int
    report_title: Optional[str] = None
    overall_grade: Optional[str] = None
    score: Optional[Decimal] = None
    summary: Optional[str] = None
    risk_summary: Optional[str] = None
    legal_case_summary: Optional[str] = None
    recommendation_note: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class FundDetailResponse(BaseModel):
    fund: FundResponse
    latest_nav: Optional[Decimal] = None
    latest_metric: Optional[FundMetricResponse] = None
    risk_alerts: List[RiskAlertResponse] = []
    legal_cases: List[LegalCaseResponse] = []
    latest_report: Optional[ReviewReportResponse] = None
    price_history: List[FundPriceResponse] = []


class FundListItem(BaseModel):
    fund_code: str
    fund_name: str
    manager: Optional[str] = None
    fund_type: Optional[str] = None
    total_asset: Optional[Decimal] = None
    fee: Optional[Decimal] = None
    latest_nav: Optional[Decimal] = None
    cumulative_return: Optional[Decimal] = None
    annual_volatility: Optional[Decimal] = None
    modified_sharpe_ratio: Optional[Decimal] = None
    sharpe_ratio: Optional[Decimal] = None
    max_drawdown: Optional[Decimal] = None
    risk_count: int = 0
    has_high_risk: bool = False
    kfr_grade: Optional[str] = None       # KFR 1~5등급
    kfr_score: Optional[Decimal] = None   # 유형 내 %순위

    model_config = {"from_attributes": True}


class UploadResponse(BaseModel):
    message: str
    funds_created: int
    funds_updated: int
    prices_inserted: int


class AnalyzeResponse(BaseModel):
    fund_code: str
    metrics: Optional[FundMetricResponse] = None
    risks: List[RiskAlertResponse] = []
    cases_found: int = 0
    report: Optional[ReviewReportResponse] = None
