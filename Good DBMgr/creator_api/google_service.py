import googlemaps
import time
from typing import List
from .datas.data import Data
from .datas.constants import TEST_MODE, GATHER_MODE
from .naver_service import NaverService
from .api_key import get_key

class GoogleService():
    def __init__(self, mode=TEST_MODE):
        # Google Maps 클라이언트 초기화 
        self.gmaps = googlemaps.Client(key=get_key("GOOGLE_API_KEY"))
        self.mode = mode

    # 구글로 맛집 검색
    def google_crawling(self, query: str = "검색어", 
                        region: str = "지역") -> List[Data]:
        """
        이전 함수명 fetch_top_restaurants_nearby
        """
        results = []
        next_page_token = None
        page_count = 0
        
        while True:
            if next_page_token:
                time.sleep(2)  # API 요청 사이에 잠시 대기
                places_result = self.gmaps.places(query=f"{region} {query}", page_token=next_page_token)
            else:
                places_result = self.gmaps.places(query=f"{region} {query}")

            page_count += 1

            for place in places_result['results']:
                place_id = place.get('place_id', 'None')
                place_details = self.gmaps.place(place_id=place_id, language='ko',
                                            fields=['name', 'url', 'vicinity', 'rating',
                                                    'user_ratings_total', 'price_level', 'reviews'])['result']

                name = place_details.get('name', '이름 없음')
                address = place_details.get('vicinity', '주소 없음')
                google_json = place_details

                # 네이버 블로그에서 해당 식당 이름으로 검색한 데이터 가져오기
                blog_datas = NaverService().crawling_naver_blog_data(query=name, region=region)

                results.append(Data(name, address, google_json, blog_datas))
            
            if self.mode == TEST_MODE:
                break  # TEST_MODE에서는 첫 페이지만 크롤링

            next_page_token = places_result.get('next_page_token')
            if not next_page_token or (self.mode == GATHER_MODE and page_count >= 3):
                break  # GATHER_MODE에서는 최대 3페이지까지 크롤링 (약 60개 결과)

        return results