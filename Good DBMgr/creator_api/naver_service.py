import requests
from urllib import parse
from typing import List
from bs4 import BeautifulSoup
from .datas.naver_data import NaverData
from .api_key import get_key

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
                blog=self.make_naver_data(blog_url=link)

                if blog is not None:
                    blogs.append(blog)
            
            return blogs[:3]

        except requests.exceptions.RequestException as e:
            print(f"Naver API 요청 실패: {str(e)}")
            return "네이버 블로그 설명 오류"
        
    def make_naver_data(self, blog_url : str) -> NaverData: 
        """
        추출이 안되면 None 반환
        """
        # url로 request를 보내서 response를 받아온다
        response = requests.get(blog_url)
        # python의 내부 html.parser로 html 전문을 파싱해서 가져온다.
        soup = BeautifulSoup(response.text, 'html.parser')

        # <iframe></iframe>식의 태그를 문서 내부에서 찾는다.
        # 여러 개를 가져오는지 제일 처음 하나를 가져오는지는 잘 모르겠다
        iframe_tag = soup.find('iframe')
        # iframe은 html안에 다른 html을 요청하는 것. 그래서 그 html의 주소는 src.
        # src 속성 추출
        iframe_src = iframe_tag['src'] if iframe_tag else None

        naver_blog_url = 'https://blog.naver.com/'

        # iframe이 가리키는 URL에 대해 별도로 요청
        if iframe_src != None:
            iframe_response_url = naver_blog_url + iframe_src
            iframe_response = requests.get(iframe_response_url)
            iframe_soup = BeautifulSoup(iframe_response.text, 'html.parser')
            
            # class="se-main-container"를 가진 <div> 태그 찾기
            div_container = iframe_soup.find('div', class_='se-main-container')
            refined_content = str()
            if div_container:
                refined_content = div_container.text.replace('\n', ' ')

            data = NaverData(content=refined_content, link=blog_url)
            return data
        
        return None


    
    
