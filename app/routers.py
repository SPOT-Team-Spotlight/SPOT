from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .vectorRouter.FaissVectorStore import FaissVectorStore
from .vectorRouter.vectorMgr import get_openai_embedding
from app.promptMgr import summarize_desc
import faiss
import numpy as np
import asyncio
import re
# FAISS 설정
dimension = 768
index = faiss.IndexFlatL2(dimension)

# FastAPI의 APIRouter 인스턴스 생성
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

vector_store = FaissVectorStore()

# GET 요청 처리, 메인 페이지 렌더링
@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# POST 요청을 통해 검색을 처리하는 엔드포인트
@router.post("/search/", response_class=HTMLResponse)
async def search_restaurant(request: Request, search_input: str = Form(...)):
    if not search_input:
        raise HTTPException(status_code=400, detail="검색어를 입력하세요.")

    print(f"검색어: {search_input}")

    embedding = get_openai_embedding(search_input)
    if vector_store.dim is None:
        print("경고: 벡터 저장소가 비어 있습니다. 먼저 데이터를 추가해주세요.")

    # embedding이 1차원 배열인지 확인
    if embedding.ndim == 1:
    # padding을 추가하여 차원을 맞춤
        padding = np.zeros(max(0, vector_store.dim - len(embedding)), dtype=np.float32)
        embedding = np.concatenate([embedding, padding])
    elif embedding.ndim == 2:
    # embedding이 이미 2차원 배열인 경우, 첫 번째 차원의 크기가 1인지 확인
        if embedding.shape[0] == 1:
            embedding = embedding.flatten()  # 1차원 배열로 변환
        else:
            raise ValueError("Unexpected embedding shape")

    # padding을 추가하여 차원을 맞춤
        padding = np.zeros(max(0, vector_store.dim - len(embedding)), dtype=np.float32)
        embedding = np.concatenate([embedding, padding])
    else:
        raise ValueError("Unexpected embedding dimensions")

    # embedding을 2차원 배열로 변환 (search 함수에 맞게)
    embedding = embedding.reshape(1, -1)

    D, I = vector_store.search(embedding, k=5)

    results = []

    for idx, i in enumerate(I[0]):
        if i < len(vector_store.metadata):
            meta = vector_store.metadata[i]
            summary = summarize_desc(meta.get("title", "Unknown"), meta.get("summary", ""))
            results.append({
                "title": meta.get("title", "Unknown"),
                "similarity": float(D[0][idx]),
                "summary": summary
            })
    print(results)
    # 검색 결과 렌더링
    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": results  # 템플릿에 검색 결과 전달
    })
    
