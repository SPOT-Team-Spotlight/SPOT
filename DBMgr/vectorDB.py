import os
from FaissVectorStore import FaissVectorStore
import numpy as np
from dotenv import load_dotenv
from models import SearchResult
from langchain.embeddings import OpenAIEmbeddings


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
    :param text: 임베딩할 텍스트
    :return: 임베딩 벡터
    """
    embedding = embeddings.embed_query(text)
    return np.array(embedding, dtype=np.float32)

def saveToVDB(data : SearchResult,
              fk : int):
    """
    SearchResult를 VectorDB에 저장하는 함수
    :param data: 저장할 SearchResult 객체
    :param fk: RDB에 저장된 키 값

    저장하는 데이터
    - 가게명 
    - 설명
    - rdb의 pk : 파라미터 fk
    """
    review_text = ' '.join([review['text'] for review in data.reviews])
    
    # 숫자로 전환 되지 않은 것들만 벡터화
    embedding = {
        "name": get_openai_embedding(data.title),
        "address": get_openai_embedding(data.address),
        "reviews": get_openai_embedding(review_text),
        "description": get_openai_embedding(data.description),
        "rating": np.array([data.rating], dtype=np.float32),
        "views": np.array([data.views], dtype=np.float32),
        "price_level": np.array([data.price_level], dtype=np.float32),
        "serves_beer": np.array([float(data.serves_beer)], dtype=np.float32),
        "serves_wine": np.array([float(data.serves_wine)], dtype=np.float32),
#        "serves_breakfast": np.array([float(data.serves_breakfast)], dtype=np.float32),
#        "serves_brunch": np.array([float(data.serves_brunch)], dtype=np.float32),
#       "serves_lunch": np.array([float(data.serves_lunch)], dtype=np.float32),
 #       "serves_dinner": np.array([float(data.serves_dinner)], dtype=np.float32),
  #      "serves_vegetarian_food": np.array([float(data.serves_vegetarian_food)], dtype=np.float32),
   #     "takeout": np.array([float(data.takeout)], dtype=np.float32)
    }
    
    metadata = {
        "name": data.title,
        "pk": fk,
        "link":data.link,
        "google_id":data.google_id
    }
    vector_store.add_to_index(embedding, metadata)
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
            print(f"검색 결과: {meta}")
            results.append({
                "title": meta.get("name", "Unknown"),
                "similarity": float(D[0][idx]),
                "pk": meta.get("pk", "Unknown"),
                "link": meta.get("link", "Unknown"),
                "google_id": meta.get("google_id", "Unknown")
            })

    # 유사도 순으로 정렬
    results.sort(key=lambda x: x["similarity"])
    return results
