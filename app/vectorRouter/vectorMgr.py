import re
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from app.vectorRouter.exceptions import EmptySearchQueryException, EmptyVectorStoreException, NoSearchResultsException
from rank_bm25 import BM25Okapi
import os
import numpy as np
from collections import defaultdict
import time
import logging
import asyncio
from app.vectorRouter.FaissVectorStore import FaissVectorStore
from app.vectorRouter.promptMgr import generate_gpt_response  # 요약 생성 함수 가져오기
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
ner_model_name = "klue/bert-base"  # NER 모델 사용
ner_tokenizer = AutoTokenizer.from_pretrained(ner_model_name)
try:
    ner_model = AutoModelForTokenClassification.from_pretrained(ner_model_name)
except EnvironmentError:
    raise EnvironmentError("모델 'klue/bert-base'을 로드할 수 없습니다. 모델이 존재하는지 확인하거나, 올바른 토큰을 제공하세요.")
ner_pipeline = pipeline("ner", model=ner_model, tokenizer=ner_tokenizer, framework="pt", device=0 if torch.cuda.is_available() else -1)

# OpenAI 임베딩을 생성하는 함수
def get_openai_embedding(text: str):
    embedding = embeddings.embed_query(text)
    return np.array(embedding, dtype=np.float32)

# 검색어를 전처리하고 NER 수행하는 함수
def preprocess_search_input(search_input: str):
    # 기본 전처리 (키워드 추출)
    keywords = re.findall(r'\b\w+\b', search_input)
    keywords = [word for word in keywords if len(word) > 1]

    # NER 수행
    entities = ner_pipeline(search_input)
    entity_keywords = [entity['word'] for entity in entities if entity['entity'].startswith("B-")]  # 시작 엔티티만 추출

    # 중복 제거 및 결합
    keywords.extend(entity_keywords)
    keywords = list(set(keywords))
    
    return keywords

# RAG(검색 + 생성) 기반 검색 함수 (비동기)
async def search_with_rag(search_input: str, k: int = 5, bm25_weight: float = 0.5, faiss_weight: float = 0.6, threshold: float = 0.6):
    if not search_input:
        raise EmptySearchQueryException()

    logging.info("검색을 시작합니다.")
    
    try:
        # 1. 검색어 전처리 및 NER 수행
        keywords = preprocess_search_input(search_input)
        if not keywords:
            raise EmptySearchQueryException("유효한 검색 키워드가 없습니다.")
        
        logging.info(f"검색어 전처리 완료: {keywords}")
    
        # 2. BM25 검색
        bm25_scores = np.zeros(len(corpus))
        for keyword in keywords:
            tokenized_query = keyword.split(" ")
            keyword_scores = bm25.get_scores(tokenized_query)
            bm25_scores += keyword_scores

        # BM25 점수 정규화
        if np.max(bm25_scores) > 0:
            bm25_scores = bm25_scores / np.max(bm25_scores)

        # 3. FAISS 검색
        embedding = get_openai_embedding(search_input)
        
        if vector_store.dim is None:
            raise EmptyVectorStoreException("FAISS 벡터 저장소가 초기화되지 않았습니다.")

        # FAISS 검색 수행
        D, I = vector_store.search(embedding.reshape(1, -1), k=len(corpus))  # 모든 문서에 대해 검색

        # FAISS 유사도 정규화
        faiss_similarities = 1 - D[0]
        if np.max(faiss_similarities) > 0:
            faiss_similarities = faiss_similarities / np.max(faiss_similarities)

        # 4. BM25와 FAISS 점수 결합
        combined_scores = {}

        for idx in range(len(corpus)):
            bm25_score = bm25_scores[idx] * bm25_weight
            faiss_score = faiss_similarities[np.where(I[0] == idx)[0][0]] * faiss_weight if idx in I[0] else 0
            combined_scores[idx] = bm25_score + faiss_score

        # 5. 임계값 적용 및 정렬
        # 동적으로 쓰레스홀드 조정
        filtered_scores = {}
        current_threshold = threshold

        while len(filtered_scores) < k and current_threshold > 0:
            # 5. 임계값 적용 및 정렬
            filtered_scores = {idx: score for idx, score in combined_scores.items() if score >= current_threshold}
            ranked_indices = sorted(filtered_scores, key=filtered_scores.get, reverse=True)

            # 임계값을 조정해서 더 많은 결과를 포함할 수 있도록 함 (0.05씩 줄이기)
            if len(filtered_scores) < k:
                current_threshold -= 0.01
                logging.info(f"임계값을 낮춥니다: {current_threshold:.2f} (현재 후보 개수: {len(filtered_scores)})")

                # 임계값이 0.5 이하로 내려가지 않도록 제한
                if current_threshold < 0.5:
                    current_threshold = 0.5
                    logging.info(f"임계값을 0.5로 고정합니다.")
                    break  # 더 이상 임계값을 줄이지 않도록 루프 종료

        logging.info(f"최종 임계값 적용 후 후보 개수: {len(filtered_scores)}")

        # 6. 미리 인덱싱한 메타데이터 사전 생성
        metadata_index = defaultdict(dict)
        for meta in vector_store.metadata:
            data_id = meta.get("data_id")

            metadata_index[data_id]['link'] = meta.get("link", "")
            metadata_index[data_id]['name'] = meta.get("name", "Unknown")
            metadata_index[data_id]['img'] = meta.get("img")    # 디폴트 값이 없어야 html에서 not found 이미지 출력
            metadata_index[data_id]['address'] = meta.get("address", "Unknown")

        # 결과 수집 및 같은 data_id를 가진 chunk 결합
        seen = set()
        combined_results = defaultdict(list)

        for idx in ranked_indices:
            if idx < len(vector_store.metadata):
                meta = vector_store.metadata[idx]
                data_id = meta.get("data_id")

                if data_id in seen:
                    continue
                seen.add(data_id)

                # 해당 data_id로 그룹화된 모든 유효한 chunk_content를 수집
                for m in vector_store.metadata:
                    if m.get("data_id") == data_id:
                        chunk_content = m.get("chunk_content", "")
                        if chunk_content:
                            combined_results[data_id].append(chunk_content)

                if len(combined_results) >= k:
                    break

        logging.info(f"선택된 결과 수: {len(combined_results)}")

        # 7. 비동기 요약 생성
        selected_results = []
        unique_names = set()

        start_time = time.time()
        
        tasks = []
        for data_id, chunks in combined_results.items():
            full_content = " ".join(chunks)

            # 인덱스를 사용하여 링크, 이름, 주소 빠르게 조회
            meta_info = metadata_index.get(data_id, {})
            link = meta_info.get('link', '')
            name = meta_info.get('name', 'Unknown')
            address = meta_info.get('address', 'Unknown')
            img = meta_info.get('img')

            if name in unique_names:
                continue
            unique_names.add(name)

            logging.info(f"선택된 링크: {link}")

            # 비동기 요약 생성 요청 추가
            task = generate_gpt_response(name, full_content)
            tasks.append(task)

            selected_results.append({
                "name": name,
                "summary": "",  # 요약 생성 후 채워질 예정
                "address": address,
                "data_id": data_id,
                "image": image_url_to_base64(img),
                "link": link
            })

        # 비동기 요약 생성 완료 대기
        summaries = await asyncio.gather(*tasks)

        # 요약을 결과에 추가
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