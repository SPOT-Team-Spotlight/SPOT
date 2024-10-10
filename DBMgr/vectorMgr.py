import os
from vectorStore.FaissVectorStore import FaissVectorStore
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings  # 새로운 모듈에서 임포트
from langchain.schema import Document
import numpy as np
from crawling.datas.data import Data

# .env 파일에서 API 키 로드 (환경 변수 설정)
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 임베딩 객체 생성
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-3-small")

# Faiss 벡터 스토어 인스턴스 생성
vector_store = FaissVectorStore()

# 텍스트 임베딩 함수
def get_openai_embedding(text): 
    """
    OpenAI를 통해 자연어 임베딩을 생성하는 함수
    :param text: 임베딩 할 텍스트
    :return: 임베딩 벡터
    """
    embedding = embeddings.embed_query(text)
    return np.array(embedding, dtype=np.float32)


def saveToVDB(data: Data):
    """
    data로 받은 객체를 VectorDB에 저장하는 함수
    """
    # 가중치를 적용하는 필드 (임베딩 * weights[""])으로 적용
    weights = {
        "location": 3.0,
        "type": 3.0,
        "menu": 3.0,
        "other": 1.0
    }
    # 필드별로 텍스트를 임베딩
    vectorization = {
        "service_list": get_openai_embedding(' '.join([f"{k}: {v}" for k, v in data.service_list.items()])),
        # 서비스 리스트 임베딩
        "reviews": get_openai_embedding(' '.join([r.page_content for r in data.reviews])),  # 리뷰 임베딩
        "price_level": get_openai_embedding(str(data.price_level)),  # 가격대 임베딩 (문자열로 변환)
        "naver_description": get_openai_embedding(' '.join([d.page_content for d in data.naver_description])),
        # 네이버 블로그 설명 임베딩
        "naver_category": get_openai_embedding(str(data.category)) * weights["menu"]

    }
    print(f"Processing text: {str(data.category)}")
    # 메타데이터 저장
    metadata = {
        "title": data.title,
        "service_list": data.service_list,
        "reviews": [r.page_content for r in data.reviews],  # 리뷰의 텍스트
        "price_level": str(data.price_level),  # 가격대 문자열로 변환하여 저장
        "naver_description": ' '.join([d.page_content for d in data.naver_description]),  # 네이버 블로그 설명 텍스트
        "summary": data.summary,
        "link": data.link
    }

    # 벡터와 메타데이터를 함께 저장
    vector_store.add_to_index(vectorization, metadata)
    vector_store.save_index()


def searchVDB(query : str = "검색할 문장",
              search_amount : int = 5): 
    """
    VectorDB에서 검색하는 함수
    :param query: 검색할 쿼리 문장
    :param search_amount: 반환할 결과의 개수
    :return: 검색 결과 리스트 list<dict>
    """
    query_embedding = get_openai_embedding(query)
    
    if vector_store.dim is None:
        print("경고: 벡터 저장소가 비어 있습니다. 먼저 데이터를 추가해주세요.")
        return []
    padding = np.zeros(vector_store.dim - len(query_embedding), dtype=np.float32)
    query_embedding = np.concatenate([query_embedding, padding])
    D, I = vector_store.search(query_embedding, k=search_amount)
    results = []

    for idx, i in enumerate(I[0]):

        if i < len(vector_store.metadata):
            meta = vector_store.metadata[i]
            results.append({
                "title": meta.get("title", "Unknown"),
                "similarity": float(D[0][idx]),
                "reviews": meta.get("reviews","Unknown"),
                "service_list": meta.get("service_list", "Unknown"),
                "summary": meta.get("summary", "Unknown"),
                "link":meta.get("link","https://none")
            })

    # 유사도 순으로 정렬
    results.sort(key=lambda x: x["similarity"])
    return results

def view_vdb_data():
    """
    VDB에 저장된 모든 데이터를 확인하는 함수
    """
    if len(vector_store.metadata) == 0:
        print("경고: VDB가 비어 있습니다.")
        return

    for idx, meta in enumerate(vector_store.metadata):
        print(f"Data {idx + 1}:")
        print(f"Title: {meta.get('title', 'Unknown')}")
        print(f"Service List: {meta.get('service_list', 'Unknown')}")
        print(f"Reviews: {meta.get('reviews', 'Unknown')}")
        print(f"Price Level: {meta.get('price_level', 'Unknown')}")
        print(f"Naver Description: {meta.get('naver_description', 'Unknown')}")
        print(f"Summary: {meta.get('summary', 'Unknown')}")
        print(f"Link: {meta.get('link', 'https://none')}")
        print("\n---\n")
