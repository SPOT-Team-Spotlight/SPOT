# 모든 크롤링을 시도하여 txt파일로 뽑아내는 코드
#from .naver_service import crawling_naver_blog_data
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .utils import clean_html
from .datas.data import Data
from .summarizer import do_summarize
from langchain.schema import Document  # 문서 객체가 필요하다면 임포트
from .google_service import fetch_top_restaurants_nearby

def start_crawling(keyword : str, region : str) -> list:
    """
    네이버 블로그에서 크롤링을 해서 돌려주는 함수
    """
   # result = crawling_naver_blog_data(query=keyword, region=region)
    result = fetch_top_restaurants_nearby(query=keyword, region=region)
    return result


def make_datas(datas: list) -> list:
    """
    가져온 정보들을 Class Data로 바꿔주는 함수
    """
    result = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=350, chunk_overlap=100)

    for d in datas:
        clean_title = clean_html(d.title)

        # 리뷰 및 블로그 설명을 청킹하여 벡터화할 준비
        clean_reviews = clean_html(' '.join(d.reviews))
        clean_naver_description = clean_html(d.naver_description)

        # 리뷰와 블로그 설명을 각각 청킹
        review_doc = Document(page_content=clean_reviews)
        naver_desc_doc = Document(page_content=clean_naver_description)

        # 문서 청킹
        chunked_reviews = text_splitter.split_documents([review_doc])
        chunked_naver_description = text_splitter.split_documents([naver_desc_doc])

        # Data 객체로 변환
        result.append(Data(
            title=clean_title,
            service_list=d.service_list,
            reviews=chunked_reviews,
            price_level=d.price_level,
            naver_description=chunked_naver_description,
            summary=do_summarize(name=clean_title, descs=chunked_naver_description, reviews=clean_reviews),
            link=d.link,
            types=d.types,
            category=d.category# 수정
        ))
        print("data:",Data)
    return result