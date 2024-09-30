# 모든 크롤링을 시도하여 txt파일로 뽑아내는 코드
from .naver_service import crawling_naver_blog_data
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .utils import clean_html
from .datas.data import Data
from .summarizer import do_summarize
from langchain.schema import Document  # 문서 객체가 필요하다면 임포트

def start_crawling(keyword : str, region : str) -> list:
    """
    네이버 블로그에서 크롤링을 해서 돌려주는 함수
    """
    result = crawling_naver_blog_data(query=keyword, region=region)
    
    return result

def make_datas(datas : list) -> list:
    """
    가져온 정보들을 Class Data로 바꿔주는 함수
    """
    result = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
    for d in datas:
        clean_title=clean_html(d['title'])
        clean_desc=clean_html(d['description'])

        # 청킹하기 위해 네이버 blog의 설명만 떼서 컨텐츠로 전달
        doc=Document(page_content=clean_desc) 
        
        # document 타입을 청킹
        chunked_list=text_splitter.split_documents([doc])

        result.append(Data(
            title=clean_title, 
            chunked_desc=chunked_list,  
            summary=do_summarize(name=clean_title, descs=chunked_list),
            link=d['link'])
        )

    return result