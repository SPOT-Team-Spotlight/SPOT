from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings  # 새로운 모듈에서 임포트
from rank_bm25 import BM25Okapi
import os
import numpy as np
from .FaissVectorStore import FaissVectorStore
from .promptMgr import summarize_desc
from .exceptions import EmptySearchQueryException, NoSearchResultsException, EmptyVectorStoreException

# .env 파일에서 API 키 로드 (환경 변수 설정)
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 임베딩 객체 생성
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-3-small")

# 벡터 저장소 인스턴스 생성
vector_store = FaissVectorStore()

# BM25 모델 초기화 (vector_store에 있는 문서들의 텍스트 사용)
corpus = [meta.get("summary", " ") for meta in vector_store.metadata]

if not corpus:
    raise EmptyVectorStoreException("메타 데이터 안에 desc가 없습니다")

tokenized_corpus = [doc.split(" ") for doc in corpus]
bm25 = BM25Okapi(tokenized_corpus)

# 텍스트 임베딩 함수
def get_openai_embedding(text: str): 
    """
    OpenAI를 통해 자연어 임베딩을 생성하는 함수
    :param text: 임베딩 할 텍스트
    :return: 임베딩 벡터
    """
    embedding = embeddings.embed_query(text)
    return np.array(embedding, dtype=np.float32)

# 서치 함수
def search(search_input: str, k: int = 5):
    """
    주어진 검색어에 대해 유사한 항목을 검색하는 함수
    :param search_input: 검색어
    :param k: 반환할 결과의 수
    :return: 검색 결과 리스트
    """
    if not search_input:
        raise EmptySearchQueryException()

    # 1. BM25 검색을 먼저 수행 (텍스트 기반 검색)
    tokenized_query = search_input.split(" ")
    bm25_scores = bm25.get_scores(tokenized_query)  # BM25 점수 계산
    top_bm25_indices = np.argsort(bm25_scores)[-10:]  # 상위 10개의 문서 인덱스 선택

    if len(top_bm25_indices) == 0:
        raise NoSearchResultsException()
    
    # 2. 검색어에 대한 
    # 임베딩 생성 (OpenAI 사용)
    embedding = get_openai_embedding(search_input)
    if vector_store.dim is None:
        raise EmptyVectorStoreException()

    # 임베딩 차원 조정
    if embedding.ndim == 1:
        padding = np.zeros(max(0, vector_store.dim - len(embedding)), dtype=np.float32)
        embedding = np.concatenate([embedding, padding])
    elif embedding.ndim == 2:
        if embedding.shape[0] == 1:
            embedding = embedding.flatten()
        else:
            raise ValueError("예상치 못한 임베딩 차원입니다.")
    else:
        raise ValueError("예상치 못한 임베딩 차원입니다.")
    
    # 임베딩을 2차원 배열로 변환
    embedding = embedding.reshape(1, -1)

    # 3. FAISS 벡터 검색 수행 (BM25로 필터링된 상위 문서들에 대해 검색)
    D, I = vector_store.search(embedding, k=k) # FAISS 인덱스에서 검색
    
    # 4. FAISS 결과와 BM25 결과를 결합하여 최종 상위 결과 선택
    final_ranked_indices = list(set(top_bm25_indices).intersection(set(I[0])))  # BM25와 FAISS의 교집합을 사용
    if not final_ranked_indices:
        final_ranked_indices = top_bm25_indices[:5]  # 교집합이 없으면 BM25의 상위 5개 문서 사용
    
     # 5. 결과를 사용자의 검색어와 맞는 형태로 요약 및 출력
    results = []
    for idx, i in enumerate(final_ranked_indices):
        if i < len(vector_store.metadata):
            meta = vector_store.metadata[i]
            summary = summarize_desc(meta.get("title", "Unknown"), meta.get("summary", ""))
            results.append({
                "title": meta.get("title", "Unknown"),
                "similarity": float(D[0][idx]),
                "summary": summary,
                "link": meta.get("link", "https://none")
            })

    return results
