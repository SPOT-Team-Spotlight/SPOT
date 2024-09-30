import requests
from urllib import parse
from typing import List
from .utils import clean_html
from .datas.config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

# 지역 필터링 함수: 지역명이 제목 또는 설명에 포함된 블로그만 반환
def filter_by_region(items: List[dict], region: str) -> List[dict]:
    filtered_items = []

    for item in items:
        title = clean_html(item['title'])
        description = clean_html(item['description'])

        # 지역명이 제목 또는 설명에 포함되어 있는지 확인
        if region in title or region in description:
            filtered_items.append(item)

    return filtered_items

def crawling_naver_blog_data(query: str = "검색 할 단어 ", 
                          region: str = "지역") -> list:
    """
    네이버 블로그 데이터 최대한 많이 (최대100개) 가져오기
    """
    try:
        # 지역과 검색어를 결합하여 검색
        combined_query = f"{region} {query}"
        enc_text = parse.quote(combined_query)
        base_url = "https://openapi.naver.com/v1/search/blog.json"

        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }

        start = 1
        display = 10
        sort = "sim"

        url = f"{base_url}?query={enc_text}&display={display}&start={start}&sort={sort}"
        combined_query = f"{region} {query}"
        enc_text = parse.quote(combined_query)

        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }

        # 네이버 블로그 API 호출
        response = requests.get(url, headers=headers)
        response.raise_for_status() 

        items = response.json().get("items", [])

        # 지역 필터링 적용
        filtered_items = filter_by_region(items, region)

        return filtered_items
    
    except requests.exceptions.RequestException as e:
        print(f"Naver API 요청 실패: {str(e)}")
        return []
    
    except Exception as e:
        print(f"네이버 블로그 데이터를 처리하는 중 오류가 발생했습니다: {str(e)}")
        return []