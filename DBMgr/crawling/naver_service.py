import requests
import re
from urllib import parse
from typing import List
# from models import SearchResult
from utils import clean_html, clean_word
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

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
        display = 100
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
        error = response.json().get("result")

        # 지역 필터링 적용
        filtered_items = filter_by_region(items, region)

        return filtered_items
    
    except requests.exceptions.RequestException as e:
        print(f"Naver API 요청 실패: {str(e)}")
        return []
    
    except Exception as e:
        print(f"네이버 블로그 데이터를 처리하는 중 오류가 발생했습니다: {str(e)}")
        return []

def crawling_naver_local_data(query: str = "검색 할 단어 ", 
                          region: str = "지역") -> list:
    """
    네이버 지도 데이터 가져오기
    현재 최대 수는 5까지만
    """
    try:
        # 지역과 검색어를 결합하여 검색
        combined_query = f"{region} {query}"
        enc_text = parse.quote(combined_query)
        base_url = "https://openapi.naver.com/v1/search/local"
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }

        results = []
        start = 1
        display = 5 
        sort = "comment"

        url = f"{base_url}?query={enc_text}&display={display}&start={start}&sort={sort}"

        while len(results) < number:
            # 네이버 블로그 API 호출
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            items = response.json().get("items", [])

            if not items:
                break

            for item in items:
                results.append(SearchResult(
                    title=clean_html(item.get('title', None)),
                    link=item.get('link', None),
                    description=item.get('description', None),
                    category=clean_word(item.get('category', None)),
                    address=item.get('roadAddress', None)
                ))

            start += display

            if len(results) >= number or len(items) < display:
                break

        return results[:number]

    except requests.exceptions.RequestException as e:
        print(f"Naver API 요청 실패: {str(e)}")
        return []
    except Exception as e:
        print(f"네이버 블로그 데이터를 처리하는 중 오류가 발생했습니다: {str(e)}")
        return []
