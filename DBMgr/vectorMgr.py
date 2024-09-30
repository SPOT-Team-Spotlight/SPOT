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
    :param data: 저장할 객체
    """
    
    # 숫자로 전환 되지 않은 것들만 벡터화
    vectorization_desc = {}
    for i, des in enumerate(data.desc):
        # Document 객체에서 텍스트 내용을 추출
        text_content = des.page_content if isinstance(des, Document) else str(des)
        vectorization_desc[i] = get_openai_embedding(text_content)  # 인덱스를 키로 사용
    
    metadata = {
        "title": data.title,
        "desc": [d.page_content if isinstance(d, Document) else str(d) for d in data.desc],
        "summary": data.summary,
        "link": data.link
    }

    # 벡터와 메타데이터를 함께 저장
    vector_store.add_to_index(vectorization_desc, metadata)
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
                "summary": meta.get("summary", "Unknown"),
                "link":meta.get("link","https://none")
            })

    # 유사도 순으로 정렬
    results.sort(key=lambda x: x["similarity"])
    return results
