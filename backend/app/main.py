"""
SecureScan - Web Security Vulnerability Scanner
Main application entry point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import time

from app.core.config import settings
from app.core.database import init_db
from app.api.router import api_router

# Import models to register them with SQLAlchemy
from app.models import user, scan, vulnerability


# Korean error message translations
ERROR_MESSAGES = {
    "value_error.email": "올바른 이메일 형식이 아닙니다",
    "value_error.missing": "필수 항목입니다",
    "string_too_short": "최소 {min_length}자 이상이어야 합니다",
    "string_too_long": "최대 {max_length}자 이하여야 합니다",
    "value_error": "입력값이 올바르지 않습니다",
}


def get_korean_error_message(error: dict) -> str:
    """Convert validation error to Korean message"""
    error_type = error.get("type", "")
    msg = error.get("msg", "")
    ctx = error.get("ctx", {})
    
    # 이미 한국어 메시지인 경우 (커스텀 validator에서 온 경우)
    if any(ord(c) > 127 for c in msg):
        return msg
    
    # 필드명 한글화
    field_names = {
        "email": "이메일",
        "username": "사용자명", 
        "password": "비밀번호",
        "full_name": "이름",
        "target_url": "대상 URL",
    }
    
    loc = error.get("loc", [])
    field = loc[-1] if loc else "필드"
    field_kr = field_names.get(field, field)
    
    # 에러 타입별 메시지
    if "email" in error_type:
        return f"{field_kr}: 올바른 이메일 형식이 아닙니다"
    elif "missing" in error_type:
        return f"{field_kr}: 필수 항목입니다"
    elif "too_short" in error_type:
        min_len = ctx.get("min_length", "")
        return f"{field_kr}: 최소 {min_len}자 이상이어야 합니다"
    elif "too_long" in error_type:
        max_len = ctx.get("max_length", "")
        return f"{field_kr}: 최대 {max_len}자 이하여야 합니다"
    elif "value_error" in error_type:
        return f"{field_kr}: {msg}"
    
    return f"{field_kr}: {msg}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"🛡️ Starting {settings.app_name} v{settings.app_version}")
    await init_db()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
    ## 🛡️ SecureScan - 웹 보안 취약점 점검 서비스
    
    AI 기반 스마트 웹 보안 스캐닝 서비스입니다.
    
    ### 주요 기능
    - **자동 취약점 스캔**: SQL Injection, XSS, CSRF 등 OWASP Top 10 취약점 탐지
    - **보고서 생성**: PDF/HTML 형식의 상세 보안 보고서
    - **API 연동**: CI/CD 파이프라인 통합 지원
    
    ### 지원 취약점 유형
    - SQL Injection (SQLi)
    - Cross-Site Scripting (XSS)
    - Cross-Site Request Forgery (CSRF)
    - Server-Side Request Forgery (SSRF)
    - Local File Inclusion (LFI)
    - Security Header 검사
    
    ### 사용 방법
    1. 회원가입 후 로그인
    2. 스캔할 URL 입력
    3. 스캔 완료 후 결과 확인
    4. 보고서 다운로드
    """,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
# CORS 설정 - 배포 환경에서는 모든 origin 허용
cors_origins = settings.cors_origins
if not settings.debug:
    # 프로덕션에서는 모든 origin 허용 (또는 특정 도메인만 설정)
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True if settings.debug else False,  # * 사용 시 credentials=False
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Validation exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    
    # 에러 메시지를 한국어로 변환
    korean_errors = [get_korean_error_message(err) for err in errors]
    
    # 첫 번째 에러만 반환 (또는 모든 에러를 합쳐서 반환)
    if len(korean_errors) == 1:
        detail = korean_errors[0]
    else:
        detail = korean_errors
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": detail}
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Global exception: {exc}")  # 서버 로그에 에러 출력
    return JSONResponse(
        status_code=500,
        content={
            "detail": "서버 내부 오류가 발생했습니다.",
            "error": str(exc) if settings.debug else None
        }
    )


# Include API router
app.include_router(api_router, prefix="/api/v1")


# Health check endpoint
@app.get("/health", tags=["상태"])
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


# Root endpoint
@app.get("/", tags=["상태"])
async def root():
    """API 루트"""
    return {
        "message": f"🛡️ {settings.app_name} API에 오신 것을 환영합니다!",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

