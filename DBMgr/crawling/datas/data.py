class Data:
    title: str
    types: str #식당 분류
    service_list: dict  # 맥주, 와인, 주류 유무 등
    reviews: list  # 리뷰 정보
    price_level: str  # 가격대 정보
    naver_description: str  # 네이버 블로그 설명
    summary: str = "생성되지 않음"
    link: str

    def __init__(self, title, types, service_list, reviews, price_level, naver_description, summary, link) -> None:
        self.title = title
        self.types =types
        self.service_list = service_list
        self.reviews = reviews
        self.price_level = price_level
        self.naver_description = naver_description
        self.summary = summary
        self.link = link

    def print_data(self):
        return f"Data {{ title: {self.title},types: {self.types}, service_list: {self.service_list}, reviews: {self.reviews}, price_level: {self.price_level}, naver_description: {self.naver_description}, summary: {self.summary}, link: {self.link} }}"
