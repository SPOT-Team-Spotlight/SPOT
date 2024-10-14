import re
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from rank_bm25 import BM25Okapi
import os
import numpy as np
from collections import defaultdict
from .FaissVectorStore import FaissVectorStore
from .promptMgr import generate_gpt_response
from .exceptions import (
    EmptySearchQueryException,
    NoSearchResultsException,
    EmptyVectorStoreException,
    VectorSearchException,
)

# .env 파일에서 API 키 로드
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 임베딩 객체 생성
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 벡터 저장소 인스턴스 생성
vector_store = FaissVectorStore()

# 코퍼스 생성
corpus = [meta.get("summary", " ") for meta in vector_store.metadata]

# 코퍼스가 비어 있는 경우 예외 발생
if not corpus:
    raise EmptyVectorStoreException("메타 데이터 안에 summary가 없습니다.")

# BM25 모델 초기화
tokenized_corpus = [doc.split(" ") for doc in corpus]
bm25 = BM25Okapi(tokenized_corpus)

# OpenAI 임베딩을 생성하는 함수
def get_openai_embedding(text: str):
    embedding = embeddings.embed_query(text)
    return np.array(embedding, dtype=np.float32)

# 검색어를 전처리하는 함수
def preprocess_search_input(search_input: str):
    keywords = re.findall(r'\b\w+\b', search_input)
    keywords = [word for word in keywords if len(word) > 1]
    return keywords

# RAG(검색 + 생성) 기반 검색 함수
def search_with_rag(search_input: str, k: int = 5, bm25_weight: float = 0.6, faiss_weight: float = 0.4):
    if not search_input:
        raise EmptySearchQueryException()

    # 1. 검색어 전처리
    keywords = preprocess_search_input(search_input)

    # 2. BM25 검색
    bm25_scores = np.zeros(len(corpus))
    for keyword in keywords:
        tokenized_query = keyword.split(" ")
        keyword_scores = bm25.get_scores(tokenized_query)
        bm25_scores += keyword_scores

    # BM25 점수 정규화
    if np.max(bm25_scores) > 0:
        bm25_scores = bm25_scores / np.max(bm25_scores)

    # 상위 BM25 인덱스 선택
    top_bm25_indices = np.argsort(bm25_scores)[-200:]
    print(f"BM25 후보 개수: {len(top_bm25_indices)}")

    if len(top_bm25_indices) == 0:
        raise NoSearchResultsException()

    # 3. FAISS 검색
    embedding = get_openai_embedding(search_input)
    
    if vector_store.dim is None:
        raise EmptyVectorStoreException()

    # 생성된 벡터를 사용해 FAISS 검색을 수행하여 상위 200개의 후보 문서를 검색합니다.
    D, I = vector_store.search(embedding.reshape(1, -1), k=200)
    print(f"FAISS 후보 개수: {len(I[0])}")

    # FAISS 유사도 정규화
    faiss_similarities = 1 - D[0]
    if np.max(faiss_similarities) > 0:
        faiss_similarities = faiss_similarities / np.max(faiss_similarities)

    # 5. BM25와 FAISS 점수 결합
    combined_scores = {}

    for idx in top_bm25_indices:
        combined_scores[idx] = bm25_scores[idx] * bm25_weight

    for idx, doc_id in enumerate(I[0]):
        if doc_id in combined_scores:
            combined_scores[doc_id] += faiss_similarities[idx] * faiss_weight
        else:
            combined_scores[doc_id] = faiss_similarities[idx] * faiss_weight

    # 6. 결합된 점수로 상위 문서 선택 및 정렬
    ranked_indices = sorted(combined_scores, key=combined_scores.get, reverse=True)
    print(f"결합된 후보 개수: {len(ranked_indices)}")

    # 7. 결과 수집 및 같은 data_id를 가진 chunk 결합
    seen = set()
    combined_results = defaultdict(list)  # data_id를 기준으로 chunk_content 결합

    for idx in ranked_indices:
        if idx < len(vector_store.metadata):
            meta = vector_store.metadata[idx]
            data_id = meta.get("data_id")

            # 이미 처리된 data_id는 건너뜁니다
            if data_id in seen:
                continue
            seen.add(data_id)

            # 해당 data_id로 그룹화된 모든 유효한 chunk_content를 수집
            for m in vector_store.metadata:
                if m.get("data_id") == data_id:
                    chunk_content = m.get("chunk_content", "")
                    if chunk_content:
                        combined_results[data_id].append(chunk_content)

            # 상위 k개의 결과만 선택합니다.
            if len(combined_results) >= k:
                break

    print(f"선택된 결과 수: {len(combined_results)}")

    # 검색 결과가 k개보다 적으면 경고 메시지를 출력합니다.
    if len(combined_results) < k:
        print("경고: 검색 결과가 충분하지 않습니다. 데이터 양을 확인하세요.")

    # 8. 결합된 내용으로 요약 생성
    selected_results = []
    unique_names = set()
    for data_id, chunks in combined_results.items():
        full_content = " ".join(chunks)  # 같은 data_id의 chunk들을 하나로 결합

        # 해당 data_id의 메타데이터 중에서 link가 있는 것을 찾습니다
        link = ""
        for m in vector_store.metadata:
            if m.get("data_id") == data_id:
                temp_link = m.get("link", "")
                if temp_link and temp_link.lower() != "none":
                    link = temp_link
                    break  # 링크를 찾았으므로 더 이상 찾지 않음

        meta = next(m for m in vector_store.metadata if m.get("data_id") == data_id)
        name = meta.get("name", "Unknown")
        address = meta.get("address", "Unknown")

        # 같은 이름이 있는 경우 중복 제거
        if name in unique_names:
            continue
        unique_names.add(name)

        # 요약 생성 전에 디버깅 출력

        print(f"선택된 링크: {link}")
  

        # 요약 생성
        summary = generate_gpt_response(name, full_content)
        selected_results.append({
            "name": name,
            "summary": summary,
            "address": address,
            "data_id": data_id,
            "link": link
        })

    return {
        "generated_response": "검색 결과 요약 생성 완료",
        "results": selected_results
    }