import requests
from urllib import parse
from typing import List
from bs4 import BeautifulSoup
from .datas.naver_data import NaverData
from .api_key import get_key
from urllib.parse import urlparse, urlunparse

class NaverService():
    def __init__(self) -> None:
        self.naver_key = get_key("NAVER_CLIENT_ID")
        self.naver_secret = get_key("NAVER_CLIENT_SECRET")

    def crawling_naver_blog_data(self,
            query: str = "검색할 가게명", region :str = "검색할 지명", 
            display: int = 10) :
        """
        네이버 블로그 데이터 최대한 많이 (최대100개) 가져오기
        display : 한 구글 지역에 매칭될 수량 10~100
        """
        try:
            # 지역과 검색어를 결합하여 검색
            combined_query = f"{region} {query}"
            enc_text = parse.quote(combined_query)
            base_url = "https://openapi.naver.com/v1/search/blog.json"

            headers = {
                "X-Naver-Client-Id": self.naver_key,
                "X-Naver-Client-Secret": self.naver_secret
            }

            start = 1
            sort = "sim"

            url = f"{base_url}?query={enc_text}&display={display}&start={start}&sort={sort}"

            # 네이버 블로그 API 호출
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            items = response.json().get("items", [])
            blogs = list()
            for item in items:
                link = item.get('link')
                blog=self.bs_crawling(blog_url=link)

                if blog is not None:
                    blogs.append(blog)
            
            return blogs

        except requests.exceptions.RequestException as e:
            print(f"Naver API 요청 실패: {str(e)}")
            return "네이버 블로그 설명 오류"
        
    def bs_crawling(self, blog_url : str) -> NaverData | None:
        """
        추출이 안되면 None 반환
        """
        # 모바일 버전으로 변환
        mobile_url = self.add_mobile_prefix(blog_url)

        # url로 request를 보내서 response를 받아온다
        response = requests.get(mobile_url)
        # python의 내부 html.parser로 html 전문을 파싱해서 가져온다.
        soup = BeautifulSoup(response.text, 'html.parser')
            
        # 네이버 블로그에 내장된 지도에서 이름 가져오기
        name = soup.find('strong', class_='se-map-title')
        name2 = soup.find('div', class_='se_title')

        # 이름이 있을 경우, 즉 지도가 있을 경우만 크롤링 진행
        if name:
            return self.get_naver_data(name, 'se-map-address', blog_url, soup)
        elif name2:
            return self.get_naver_data(name2, 'se-address', blog_url, soup)
        else:
            return None

    def get_naver_data(self, name, address_class, blog_url, soup):
        refined_name = str()
        refined_name = name.text

        # 네이버 블로그에 내장된 지도에서 주소 가져오기
        address = soup.find('p', class_=address_class)
        refined_address = str()
        if address:
            refined_address = address.text

        # 네이버 블로그에 내장된 대표 이미지 찾기
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            image_url = og_image['content']

        # class="se-main-container"를 가진 <div> 태그 찾기
        div_container = soup.find('div', class_='se-main-container')
        refined_content = str()
        if div_container:   
            refined_content = div_container.text.replace('\n', ' ')

        data = NaverData(name=refined_name, address=refined_address, content=refined_content, src= image_url, link=blog_url)
        return data

    def add_mobile_prefix(self, url):
        """
        모바일 주소로 변환해서 진행함
        """
        parsed = urlparse(url)

        if parsed.netloc == 'blog.naver.com':
            new_netloc = 'm.' + parsed.netloc
            return urlunparse(parsed._replace(netloc=new_netloc))
        
        return url


    
    