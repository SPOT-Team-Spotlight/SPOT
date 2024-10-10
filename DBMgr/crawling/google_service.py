import time

import googlemaps
from typing import List
from .datas.config import GOOGLE_API_KEY
from .datas.data import Data
from .naver_service import crawling_naver_blog_data,naver_location_search
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

def fetch_top_restaurants_nearby(query: str = "검색어", region: str = "지역", max_results: int = 60) -> List[Data]:
    results = []
    page_token = None
    total_fetched = 0

    while total_fetched < max_results:
        # Google Places 텍스트 검색 요청 (next_page_token 사용)
        if page_token:
            places_result = gmaps.places(query=f"{region} {query}", page_token=page_token)
        else:
            places_result = gmaps.places(query=f"{region} {query}")

        # 검색 결과 처리
        for place in places_result['results']:
            place_id = place.get('place_id', 'None')
            types = place.get('types', [])
            place_details = gmaps.place(place_id=place_id, language='ko')['result']
            print("place_details :", place_details)
            # place_details = gmaps.place(place_id=place_id, language='ko',
            #                             fields=['name', 'url', 'vicinity', 'rating',
            #                                     'user_ratings_total', 'price_level', 'reviews',
            #                                     'serves_beer', 'serves_wine',
            #                                     'serves_breakfast', 'serves_lunch', 'serves_dinner'])['result']
            # 필요한 데이터를 리스트로 이어붙이기 위해 desc 필드에 저장
            description_list = [
                f"주소: {place_details.get('vicinity', '주소 없음')}",
                f"평점: {place_details.get('rating', 0.0)}",
                f"리뷰 수: {place_details.get('user_ratings_total', 0)}",
                f"가격대: {place_details.get('price_level', '가격 정보 없음')}",
                f"아침 제공: {'예' if place_details.get('serves_breakfast') else '아니요'}",
                f"점심 제공: {'예' if place_details.get('serves_lunch') else '아니요'}",
                f"저녁 제공: {'예' if place_details.get('serves_dinner') else '아니요'}",
                f"맥주 제공: {'예' if place_details.get('serves_beer') else '아니요'}",
                f"와인 제공: {'예' if place_details.get('serves_wine') else '아니요'}"
            ]

            service_list = {
                "맥주 제공": place_details.get('serves_beer', False),
                "와인 제공": place_details.get('serves_wine', False),
                "아침 제공": place_details.get('serves_breakfast', False),
                "점심 제공": place_details.get('serves_lunch', False),
                "저녁 제공": place_details.get('serves_dinner', False)
            }

            # 가격대
            price_level = place_details.get('price_level', '가격 정보 없음')
            reviews = [review.get('text', '리뷰 내용 없음') for review in place_details.get('reviews', [])]
            print("리뷰갯수",len(reviews))

            # 네이버 블로그에서 해당 식당 이름으로 검색한 데이터 가져오기
            naver_description = crawling_naver_blog_data(query=place_details.get('name', ''), region=region)
            naver_category = naver_location_search(query=place_details.get('name','')) # 수정하기
            description_list.append(f"네이버 블로그 설명: {naver_description}")
            print("구글검색결과:" + str(results))
            print("naver검색 결과:" + str(naver_description))
            print("네이버지역 결과:" + str(naver_category))
            # ttt = place_details.get('types', None)
            # print("types:",ttt)
            # 최종 요약 생성1

            summary = do_summarize(name=place_details.get('name', '이름 없음'), descs=[naver_description], reviews=' '.join(reviews))

            # Data 객체 생성 및 결과 리스트에 추가
            results.append(Data(
                title=place_details.get('name', '이름 없음'),
                service_list=service_list,
                reviews=reviews,
                price_level=price_level,
                naver_description=naver_description,
                summary=summary,
                link=place_details.get('url', 'URL 없음'),
                types=place.get('types','장소분류 없음'), #장소 분류 추가해1야함
                category=naver_category
            ))

            total_fetched += 1
            if total_fetched >= max_results:
                break

        # 다음 페이지로 이동할 수 있도록 next_page_token 설정
        page_token = places_result.get('next_page_token')

        # 다음 페이지가 없으면 종료
        if not page_token:
            break

        # 다음 페이지 요청 전에 잠시 대기 (next_page_token 활성화 시간 대기)
        time.sleep(2)

    return results
