from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from sqlalchemy import text, inspect

from app.database import engine, Base, SessionLocal
from app.routers import funds, metrics, risks, legal_cases, reports
from app.routers import auth as auth_router
from app.routers import admin as admin_router
from app.routers import investment as investment_router

Base.metadata.create_all(bind=engine)


def _migrate_fund_metrics():
    """fund_metrics 테이블에 KFR 신규 컬럼이 없으면 자동으로 추가 (무중단 마이그레이션)."""
    new_columns = [
        ("downside_risk",            "NUMERIC"),
        ("r_squared",                "NUMERIC"),
        ("beta",                     "NUMERIC"),
        ("tracking_error",           "NUMERIC"),
        ("modified_sharpe_ratio",    "NUMERIC"),
        ("coefficient_of_variation", "NUMERIC"),
        ("treynor_ratio",            "NUMERIC"),
        ("jensen_alpha",             "NUMERIC"),
        ("information_ratio",        "NUMERIC"),
        ("winning_ratio",            "NUMERIC"),
    ]
    inspector = inspect(engine)
    existing = {c["name"] for c in inspector.get_columns("fund_metrics")}
    with engine.begin() as conn:
        for col, col_type in new_columns:
            if col not in existing:
                conn.execute(text(f"ALTER TABLE fund_metrics ADD COLUMN {col} {col_type}"))


_migrate_fund_metrics()

# 기본 관리자 계정 seeding
def _seed_default_admin():
    from app import models
    from app.auth import hash_password
    import os

    db = SessionLocal()
    try:
        if db.query(models.User).first():
            return
        default_pw = os.getenv("INITIAL_ADMIN_PASSWORD", "FundR!sk@2024")
        admin = models.User(
            email="fundadmin@fundisk.local",
            username="fundadmin",
            hashed_password=hash_password(default_pw),
            role="admin",
        )
        db.add(admin)
        db.commit()
        print(f"[INIT] 기본 관리자 계정 생성 — 아이디: fundadmin / 비밀번호: {default_pw}")
        print("[WARN] 운영 환경에서는 반드시 비밀번호를 변경하세요.")
    finally:
        db.close()

_seed_default_admin()

app = FastAPI(
    title="CaseFund 케이스펀드",
    description="펀드 성과 분석 및 리스크 감지, 관련 판례/결정문 연계 서비스",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(funds.router, prefix="/api/funds", tags=["펀드"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["지표"])
app.include_router(risks.router, prefix="/api/risks", tags=["리스크"])
app.include_router(legal_cases.router, prefix="/api/cases", tags=["법적 사례"])
app.include_router(reports.router, prefix="/api/reports", tags=["리포트"])
app.include_router(auth_router.router, prefix="/api/auth", tags=["인증"])
app.include_router(admin_router.router, prefix="/api/admin", tags=["관리자"])
app.include_router(investment_router.router, prefix="/api/investment", tags=["투자 계획"])


@app.get("/health")
def health():
    return {"status": "ok"}


# 빌드된 프론트엔드 정적 파일 서빙 (프로덕션)
STATIC_DIR = Path(__file__).parent.parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(_: str):
        return FileResponse(STATIC_DIR / "index.html")
