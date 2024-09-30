from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, String, Integer, Boolean, Float

# from database import Base

class SearchResult(BaseModel):
    """
    검색 결과 저장되는 클래스, VO
    """
    title: str
    link: str
    address: str
    reviews : Optional[list] = None # 리뷰들, 구글 api는 list(dict)
    description: Optional[str] = None # 간략 설명
    menus : Optional[list] = None
    category: Optional[str] = None
    rating: Optional[float] = None  # 평점 
    views: Optional[int] = None     # 조회수
    price_level: Optional[int] = None   # 가격대, 구글이 제공하는대로 0~4로 구분
    """
    0 Free
    1 Inexpensive
    2 Moderate
    3 Expensive
    4 Very Expensive
    """
    google_id : Optional[str] = None
    serves_beer: Optional[bool] = None
    serves_wine: Optional[bool] = None
    #serves_breakfast: Optional[bool] = None
    serves_brunch: Optional[bool] = None
    serves_lunch: Optional[bool] = None
    serves_dinner: Optional[bool] = None
    serves_vegetarian_food: Optional[bool] = None
    takeout: Optional[bool] = None

    international_phone_number: Optional[bool] = None

# TODO: rdb에 적재
# class Restaurant(Base):
#     __tablename__ = 'restaurants'

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True)
#     address = Column(String)
#     price_level = Column(Integer, nullable=True)
#     rating = Column(Float, nullable=True) 

# class instanceData():
# TODO: 갱신이 자주 필요한 데이터 모음, google_id로 가져오기
