from .naver_data import NaverData

class Data():
    """
    크롤링한 정보들을 저장하는 클래스
    """
    name : str
    address : str
    blog_datas : list[NaverData] 
    
    # 하나의 구글 결과를 기반으로 여러 개의 리뷰와 블로그를 가져옴으로써 정확도 향상을 도모함

    def __init__(self, name, address, google_json, blog_datas = list) -> None:
        self.name = name
        self.address = address
        self.google_json = google_json
        self.vectorized_json = None
        self.blog_datas = blog_datas

    def print_data(self):
        return f"Data [name: {self.name}\n address: {self.address} \
            google_json: {self.google_json}\n blog_datas:{self.blog_datas}"
