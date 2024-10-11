from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .vectorRouter.vectorMgr import search as vector_search
from .vectorRouter.exceptions import VectorSearchException, EmptySearchQueryException, NoSearchResultsException, EmptyVectorStoreException

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

    print(f"검색 결과: {results}")
    # 검색 결과 페이지 렌더링
    return templates.TemplateResponse("results.html", {
        "request": request,
        "results": results,
        "search_input": search_input
    })