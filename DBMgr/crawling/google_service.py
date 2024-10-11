import googlemaps
from typing import List
from .datas.config import GOOGLE_API_KEY
from .datas.data import Data
from .naver_service import crawling_naver_blog_data
from .summarizer import do_summarize
# Google Maps 클라이언트 초기화
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)


# 입력한 지역(동/역)을 기반으로 좌표(위도, 경도)를 가져오는 함수
def get_location_from_region(region: str):
    geocode_result = gmaps.geocode(region)
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        return location['lat'], location['lng']
    return None, None


# 반경 1km 내에서 상위 5개의 맛집 검색
def fetch_top_restaurants_nearby(query: str = "검색어", region: str = "지역"
                                 ) -> List[Data]:
    places_result = gmaps.places(query=f"{region} {query}")

    results = []

    for place in places_result['results']:
        place_id = place.get('place_id', 'None')
        place_details = gmaps.place(place_id=place_id, language='ko',
                                    fields=['name', 'url', 'vicinity', 'rating',
                                            'user_ratings_total', 'price_level', 'reviews'])['result']
                                            # 'serves_beer', 'serves_wine',
                                            # 'serves_breakfast', 'serves_lunch', 'serves_dinner'])['result']

        # 필요한 데이터를 리스트로 이어붙이기 위해 desc 필드에 저장
        description_list = [
            f"주소: {place_details.get('vicinity', '주소 없음')}",
            f"평점: {place_details.get('rating', 0.0)}",
            f"리뷰 수: {place_details.get('user_ratings_total', 0)}",
            f"가격대: {place_details.get('price_level', '가격 정보 없음')}"
            # f"아침 제공: {'예' if place_details.get('serves_breakfast') else '아니요'}",
            # f"점심 제공: {'예' if place_details.get('serves_lunch') else '아니요'}",
            # f"저녁 제공: {'예' if place_details.get('serves_dinner') else '아니요'}",
            # f"맥주 제공: {'예' if place_details.get('serves_beer') else '아니요'}",
            # f"와인 제공: {'예' if place_details.get('serves_wine') else '아니요'}"
        ]

        # 네이버 블로그에서 해당 식당 이름으로 검색한 데이터 가져오기
        naver_description = crawling_naver_blog_data(query=place_details.get('name', ''), region=region)
        description_list.append(f"네이버 블로그 설명: {naver_description}")
        
        # 리뷰가 있으면 추가
        reviews = place_details.get('reviews', [])
        if reviews:
            review_texts = [review.get('text', '리뷰 내용 없음') for review in reviews]
            description_list.append(f"리뷰: {' '.join(review_texts)}")

        # 최종 요약 생성
        summary = do_summarize(name=place_details.get('name', '이름 없음'), descs=description_list)

        # Data 객체 생성 및 결과 리스트에 추가
        results.append(Data(
            title=place_details.get('name', '이름 없음'),
            chunked_desc=description_list,  # 결합된 description_list를 chunked_desc에 저장
            summary=summary,
            link=place_details.get('url', 'URL 없음')
        ))
    return results[:100]