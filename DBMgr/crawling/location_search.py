



def location_search(query: str, google_lat: float, google_lng: float) -> dict:
    # 네이버 API에서 검색
    url = f"https://openapi.naver.com/v1/search/local.json?query={query}"
    response = requests.get(url, headers=headers)
    items = response.json().get('items', [])

    for item in items:
        naver_lat = float(item['mapx']) / 1000000  # 네이버 좌표 형식을 변환해야 함
        naver_lng = float(item['mapy']) / 1000000

        # 좌표 비교 (100m 이내)
        if haversine(google_lat, google_lng, naver_lat, naver_lng) < 0.1:
            return {'name': item['title'], 'lat': naver_lat, 'lng': naver_lng, 'category': item['category']}
    return {'name': 'Not Found', 'lat': None, 'lng': None, 'category': 'Not Found'}