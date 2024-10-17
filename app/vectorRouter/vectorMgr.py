import re
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from app.vectorRouter.exceptions import EmptySearchQueryException, EmptyVectorStoreException
from rank_bm25 import BM25Okapi
import os
import numpy as np
from collections import defaultdict
import time
import logging
import asyncio
from app.vectorRouter.FaissVectorStore import FaissVectorStore
from app.vectorRouter.promptMgr import generate_gpt_response
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import torch
import requests
import base64

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# .env 파일에서 API 키 로드
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 임베딩 객체 생성
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 벡터 저장소 인스턴스 생성
vector_store = FaissVectorStore()

# 코퍼스 생성
corpus = [meta.get("chunk_content", " ") for meta in vector_store.metadata]

# 코퍼스가 비어 있는 경우 예외 발생
if not corpus:
    raise EmptyVectorStoreException("메타 데이터 안에 chunk_content 없습니다.")

# BM25 모델 초기화
tokenized_corpus = [doc.split(" ") for doc in corpus]
bm25 = BM25Okapi(tokenized_corpus)

# NER 모델 로드
ner_model_name = "klue/bert-base"
ner_tokenizer = AutoTokenizer.from_pretrained(ner_model_name)
try:
    ner_model = AutoModelForTokenClassification.from_pretrained(ner_model_name)
except EnvironmentError:
    raise EnvironmentError("모델 'klue/bert-base'을 로드할 수 없습니다.")
ner_pipeline = pipeline("ner", model=ner_model, tokenizer=ner_tokenizer, framework="pt", device=0 if torch.cuda.is_available() else -1)

# OpenAI 임베딩을 생성하는 함수
def get_openai_embedding(text: str):
    embedding = embeddings.embed_query(text)
    return np.array(embedding, dtype=np.float32)

# 검색어를 전처리하고 NER 수행하는 함수 (필요 없는 키워드 필터링 추가)
def preprocess_search_input(search_input: str):
    keywords = re.findall(r'\b\w+\b', search_input)
    keywords = [word for word in keywords if len(word) > 1]

    # NER 수행
    entities = ner_pipeline(search_input)
    entity_keywords = [entity['word'] for entity in entities if entity['entity'].startswith("B-")]

    keywords.extend(entity_keywords)
    
    # 중요하지 않은 단어 필터링
    filtered_keywords = [word for word in keywords if word not in ["에서", "의", "이", "가"]]
    filtered_keywords = list(set(filtered_keywords))
    
    return filtered_keywords

# RAG(검색 + 생성) 기반 검색 함수 (비동기)

async def search_with_rag(search_input: str, k: int = 7, bm25_weight: float = 1, faiss_weight: float = 1, threshold: float = 0.5):
    if not search_input:
        raise EmptySearchQueryException()

    logging.info("검색을 시작합니다.")
    
    try:
        # 검색어 전처리
        keywords = preprocess_search_input(search_input)
        if not keywords:
            raise EmptySearchQueryException("유효한 검색 키워드가 없습니다.")
        
        logging.info(f"검색어 전처리 완료: {keywords}")
    
        # BM25 검색
        bm25_scores = np.zeros(len(corpus))
        for keyword in keywords:
            tokenized_query = keyword.split(" ")
            keyword_scores = bm25.get_scores(tokenized_query)
            bm25_scores += keyword_scores

        if np.max(bm25_scores) > 0:
            bm25_scores = bm25_scores / np.max(bm25_scores)

        # 상위 K개의 문서 선택
        top_bm25_indices = np.argsort(bm25_scores)[-k:]

        # FAISS 검색
        embedding = get_openai_embedding(search_input)
        
        if vector_store.dim is None:
            raise EmptyVectorStoreException("FAISS 벡터 저장소가 초기화되지 않았습니다.")

        D, I = vector_store.search(embedding.reshape(1, -1), k=k)

        faiss_similarities = 1 - D[0]
        if np.max(faiss_similarities) > 0:
            faiss_similarities = faiss_similarities / np.max(faiss_similarities)

        # BM25와 FAISS 점수 결합 (가중치 조정)
        combined_scores = {idx: bm25_scores[idx] * bm25_weight for idx in top_bm25_indices}
        for idx, score in zip(I[0], faiss_similarities):
            if idx in combined_scores:
                combined_scores[idx] += score * faiss_weight
            else:
                combined_scores[idx] = score * faiss_weight

        # 임계값 적용 및 상위 k개의 결과 선택
        filtered_scores = {idx: score for idx, score in combined_scores.items() if score >= threshold}
        ranked_indices = sorted(filtered_scores, key=filtered_scores.get, reverse=True)

        # 결과가 충분하지 않으면 임계값을 낮추어 추가 검색
        while len(ranked_indices) < 5 and threshold > 0.1:
            threshold -= 0.1
            filtered_scores = {idx: score for idx, score in combined_scores.items() if score >= threshold}
            ranked_indices = sorted(filtered_scores, key=filtered_scores.get, reverse=True)

        # 선택된 결과가 5개 미만인 경우 추가적인 문서 선택
        if len(ranked_indices) < 5:
            additional_indices = [idx for idx in range(len(corpus)) if idx not in ranked_indices]
            ranked_indices.extend(additional_indices[:5 - len(ranked_indices)])

        logging.info(f"최종 선택된 문서 개수: {len(ranked_indices)}")

        # 메타데이터 인덱스 생성
        metadata_index = {meta.get("data_id"): {
            'link': meta.get("link", ""),
            'name': meta.get("name", "Unknown"),
            'img': meta.get("img"),
            'address': meta.get("address", "Unknown")
        } for meta in vector_store.metadata}

        # 결과 수집 및 요약 생성
        seen = set()
        combined_results = defaultdict(list)
        selected_results = []
        unique_names = set()

        start_time = time.time()
        tasks = []

        for idx in ranked_indices:
            if idx < len(vector_store.metadata):
                meta = vector_store.metadata[idx]
                data_id = meta.get("data_id")

                if data_id in seen:
                    continue
                seen.add(data_id)

                chunk_content = meta.get("chunk_content", "")
                if chunk_content:
                    combined_results[data_id].append(chunk_content)

        # 비동기 요약 생성 (모든 문서 요약을 병렬로 수행)
        for data_id, chunks in combined_results.items():
            full_content = " ".join(chunks)

            meta_info = metadata_index.get(data_id, {})
            link = meta_info.get('link', '')
            name = meta_info.get('name', 'Unknown')
            address = meta_info.get('address', 'Unknown')
            img = meta_info.get('img')

            if name in unique_names:
                continue
            unique_names.add(name)

            task = generate_gpt_response(name, full_content)
            tasks.append(task)

            selected_results.append({
                "name": name,
                "summary": "",
                "address": address,
                "data_id": data_id,
                "image": image_url_to_base64(img),
                "link": link
            })

        # 비동기 작업 병렬 실행
        summaries = await asyncio.gather(*tasks)

        for i, summary in enumerate(summaries):
            selected_results[i]['summary'] = summary

        end_time = time.time()
        logging.info(f"전체 요약 생성 소요 시간: {end_time - start_time:.2f}초")

        # 결과 로깅 (image 필드 제외)
        logged_results = {
            "generated_response": "검색 결과 요약 생성 완료",
            "results": [
                {k: v for k, v in result.items() if k != "image"}
                for result in selected_results
            ]
        }

        logging.info("검색 결과: %s", logged_results)

        return {
            "generated_response": "검색 결과 요약 생성 완료",
            "results": selected_results
        }

    except Exception as e:
        logging.error(f"검색 중 오류 발생: {str(e)}")
        raise


def image_url_to_base64(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image_binary = response.content
        image_base64 = base64.b64encode(image_binary).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"
    else:
        raise Exception(f"Failed to retrieve image. Status code: {response.status_code}")

    
    # main 블록 추가
if __name__ == "__main__":
    print("코드 실행 시작")

    # asyncio 이벤트 루프를 통해 비동기 함수 실행
    try:
        search_input = "강남역 햄버거"
        result = asyncio.run(search_with_rag(search_input, k=5))
         # 이미지 데이터 제외한 결과만 출력
        simplified_result = [
            {k: v for k, v in res.items() if k != "image"}
            for res in result["results"]
        ]
        print("검색 결과:", simplified_result)
    except Exception as e:
        print(f"검색 실행 중 오류 발생: {e}")

