from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .vectorRouter.vectorMgr import search_with_rag as vector_search
from .vectorRouter.exceptions import (
    VectorSearchException,
    EmptySearchQueryException,
    NoSearchResultsException,
    EmptyVectorStoreException,
)
import requests
from .config import NAVER_MAP_CLIENT_ID, NAVER_MAP_CLIENT_SECRET

# FastAPI의 APIRouter 인스턴스 생성
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# GET 요청 처리, 메인 페이지 렌더링
@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})



# POST 요청을 통해 검색을 처리하는 엔드포인트에 하이브리드 검색 추가
@router.post("/search/", response_class=HTMLResponse)
async def search_restaurant(request: Request, search_input: str = Form(...)):
    print(f"검색 입력: {search_input}")
    try:
        results = vector_search(search_input)
    except EmptySearchQueryException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NoSearchResultsException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except EmptyVectorStoreException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except VectorSearchException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"예상치 못한 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

    print(f"검색 결과: {results}")
    # 검색 결과 페이지 렌더링
    return templates.TemplateResponse("results.html", {
        "request": request,
        "results": results["results"],
        "generated_response": results["generated_response"],
        "search_input": search_input

    })

# 네이버 지오코딩을 처리하는 엔드포인트 추가
@router.get("/geocode")
async def geocode(address: str):
    headers = {
        "X-NCP-APIGW-API-KEY-ID": NAVER_MAP_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": NAVER_MAP_CLIENT_SECRET
    }
    try:
        response = requests.get(
            f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={address}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))