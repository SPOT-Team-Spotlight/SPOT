import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .routers import router

# 로그 레벨 설정
logging.basicConfig(level=logging.WARNING)

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(debug=True)

# 라우터 등록
app.include_router(router)

# 정적 파일 및 템플릿 경로 설정
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# CORS 설정 - 모든 도메인에서 접근 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 접근 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)