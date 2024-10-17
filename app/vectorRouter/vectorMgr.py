import re  # 정규 표현식 모듈
from dotenv import load_dotenv  # .env 파일의 환경 변수를 로드하기 위한 모듈
from langchain_openai import OpenAIEmbeddings  # OpenAI 임베딩을 사용하기 위한 모듈
from app.vectorRouter.exceptions import EmptySearchQueryException, EmptyVectorStoreException, NoSearchResultsException  # 사용자 정의 예외 처리 모듈
from rank_bm25 import BM25Okapi  # BM25 모델을 사용하기 위한 모듈
import os  # 운영체제 관련 모듈
import numpy as np  # 배열 연산을 위한 라이브러리
from collections import defaultdict  # 기본값이 있는 딕셔너리를 사용하기 위한 모듈
import time  # 시간 측정 모듈
import logging  # 로깅 모듈
import asyncio  # 비동기 처리를 위한 모듈
from app.vectorRouter.FaissVectorStore import FaissVectorStore  # FAISS 벡터 저장소 클래스
from app.vectorRouter.promptMgr import generate_gpt_response  # OpenAI API를 호출하는 함수
from transformers import AutoTokenizer, AutoModelForTokenClassification  # BERT 모델과 토크나이저 사용
from transformers import pipeline  # 파이프라인을 사용하여 NLP 모델 적용
import torch  # PyTorch 딥러닝 라이브러리
import requests  # HTTP 요청을 위한 모듈
import base64  # 이미지를 base64 형식으로 인코딩하기 위한 모듈
import aiohttp  # 비동기 HTTP 요청 모듈


# 코드 설명 요약:
# 환경설정 및 임베딩 생성: .env 파일에서 OpenAI API 키를 로드하고, OpenAI 임베딩 객체를 생성합니다.
# 검색어 전처리 및 NER 수행: 검색어를 정규 표현식을 통해 전처리하고, NER(Named Entity Recognition) 모델을 사용하여 엔티티 키워드를 추출합니다.
# BM25 및 FAISS 검색 수행: BM25와 FAISS를 결합하여 검색 점수를 계산하고, 이를 바탕으로 상위 문서를 선택합니다.
# 비동기 요약 생성: 검색된 문서에 대해 OpenAI API를 통해 비동기적으로 요약을 생성하고, 결과를 반환합니다.
# 이미지 처리: 이미지 URL을 base64로 변환하여 반환합니다.

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# .env 파일에서 API 키 로드
load_dotenv()  # 환경 변수를 로드하여 사용
openai_api_key = os.getenv("OPENAI_API_KEY")  # .env 파일에서 OpenAI API 키를 가져옴

# OpenAI 임베딩 객체 생성
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")  # OpenAI의 텍스트 임베딩 모델 사용

# 벡터 저장소 인스턴스 생성
vector_store = FaissVectorStore()  # FAISS 벡터 저장소 인스턴스 초기화

# 코퍼스 생성 (벡터 저장소에서 가져온 데이터로 텍스트 목록 생성)
corpus = [meta.get("chunk_content", " ") for meta in vector_store.metadata]

# 코퍼스가 비어 있는 경우 예외 발생
if not corpus:
    raise EmptyVectorStoreException("메타 데이터 안에 chunk_content 없습니다.")  # 벡터 저장소가 비어 있을 경우 예외 발생

# BM25 모델 초기화
tokenized_corpus = [doc.split(" ") for doc in corpus]  # 코퍼스를 공백으로 토큰화
bm25 = BM25Okapi(tokenized_corpus)  # BM25 모델 초기화

# NER 모델 로드 (KLUE BERT 사용)
ner_model_name = "klue/bert-base"  # 한국어 NER을 위한 BERT 모델
ner_tokenizer = AutoTokenizer.from_pretrained(ner_model_name)  # 토크나이저 로드
try:
    ner_model = AutoModelForTokenClassification.from_pretrained(ner_model_name)  # 모델 로드
except EnvironmentError:
    raise EnvironmentError("모델 'klue/bert-base'을 로드할 수 없습니다.")  # 모델 로드 실패 시 예외 발생

# NER(Named Entity Recognition) 파이프라인 생성
ner_pipeline = pipeline("ner", model=ner_model, tokenizer=ner_tokenizer, framework="pt", device=0 if torch.cuda.is_available() else -1)  # PyTorch 기반 NER 파이프라인 생성

# OpenAI 임베딩을 생성하는 함수
def get_openai_embedding(text: str):
    embedding = embeddings.embed_query(text)  # OpenAI API로 임베딩 생성
    return np.array(embedding, dtype=np.float32)  # NumPy 배열로 반환

# 검색어를 전처리하고 NER 수행하는 함수 (필요 없는 키워드 필터링 추가)
def preprocess_search_input(search_input: str):
    # 검색어에서 단어를 추출
    keywords = re.findall(r'\b\w+\b', search_input)
    keywords = [word for word in keywords if len(word) > 1]  # 한 글자짜리 단어 제외

    # NER 수행
    entities = ner_pipeline(search_input)
    entity_keywords = [entity['word'] for entity in entities if entity['entity'].startswith("B-")]  # B-로 시작하는 엔티티만 추출

    # NER 키워드를 기존 키워드 리스트에 추가
    keywords.extend(entity_keywords)
    
    # 중요하지 않은 단어 필터링
    filtered_keywords = [word for word in keywords if word not in ["에서", "의", "이", "가"]]  # 필요 없는 단어 제거
    filtered_keywords = list(set(filtered_keywords))  # 중복 제거
    
    return filtered_keywords  # 전처리된 키워드 반환

# RAG(검색 + 생성) 기반 검색 함수 (비동기)
async def search_with_rag(search_input: str, k: int = 5, bm25_weight: float = 1, faiss_weight: float = 1, threshold: float = 0.6):
    if not search_input:
        raise EmptySearchQueryException()  # 검색어가 없을 경우 예외 발생

    logging.info("검색을 시작합니다.")  # 검색 시작 로그 출력
    
    try:
        keywords = preprocess_search_input(search_input)  # 검색어 전처리 및 NER 수행
        if not keywords:
            raise EmptySearchQueryException("유효한 검색 키워드가 없습니다.")  # 유효한 키워드가 없을 경우 예외 발생
        
        logging.info(f"검색어 전처리 완료: {keywords}")  # 전처리 완료 로그 출력
    
        # BM25 검색
        bm25_scores = np.zeros(len(corpus))  # BM25 점수를 저장할 배열 초기화
        for keyword in keywords:
            tokenized_query = keyword.split(" ")  # 키워드를 공백으로 분리하여 토큰화
            keyword_scores = bm25.get_scores(tokenized_query)  # BM25 점수 계산
            bm25_scores += keyword_scores  # 점수를 합산

        if np.max(bm25_scores) > 0:
            bm25_scores = bm25_scores / np.max(bm25_scores)  # 점수를 0~1 사이로 정규화

        # 상위 K개의 문서만 선택
        top_bm25_indices = np.argsort(bm25_scores)[-k:]  # BM25 점수가 높은 상위 K개의 문서 선택

        # FAISS 검색
        embedding = get_openai_embedding(search_input)  # 검색어 임베딩 생성
        
        if vector_store.dim is None:
            raise EmptyVectorStoreException("FAISS 벡터 저장소가 초기화되지 않았습니다.")  # FAISS 벡터 저장소가 초기화되지 않았을 경우 예외 발생

        D, I = vector_store.search(embedding.reshape(1, -1), k=k)  # FAISS 검색 수행

        faiss_similarities = 1 - D[0]  # FAISS 유사도 계산
        if np.max(faiss_similarities) > 0:
            faiss_similarities = faiss_similarities / np.max(faiss_similarities)  # 유사도 정규화

        # BM25와 FAISS 점수 결합 (가중치 조정)
        combined_scores = {}
        for idx in top_bm25_indices:
            bm25_score = bm25_scores[idx] * bm25_weight  # BM25 점수에 가중치 부여
            faiss_score = faiss_similarities[np.where(I[0] == idx)[0][0]] * faiss_weight if idx in I[0] else 0  # FAISS 점수에 가중치 부여
            combined_scores[idx] = bm25_score + faiss_score  # 두 점수를 합산

        # 임계값 적용 및 상위 k개의 결과 선택
        filtered_scores = {idx: score for idx, score in combined_scores.items() if score >= threshold}  # 임계값 이상인 문서만 선택
        ranked_indices = sorted(filtered_scores, key=filtered_scores.get, reverse=True)  # 점수에 따라 문서 정렬

        logging.info(f"최종 선택된 문서 개수: {len(ranked_indices)}")  # 선택된 문서 개수 로그 출력

        # 메타데이터 인덱스 생성
        metadata_index = defaultdict(dict)
        for meta in vector_store.metadata:
            data_id = meta.get("data_id")
            metadata_index[data_id]['link'] = meta.get("link", "")
            metadata_index[data_id]['name'] = meta.get("name", "Unknown")
            metadata_index[data_id]['img'] = meta.get("img")
            metadata_index[data_id]['address'] = meta.get("address", "Unknown")

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
                    continue  # 이미 처리한 데이터는 건너뜀
                seen.add(data_id)

                for m in vector_store.metadata:
                    if m.get("data_id") == data_id:
                        chunk_content = m.get("chunk_content", "")
                        if chunk_content:
                            combined_results[data_id].append(chunk_content)  # 결과를 수집

                if len(combined_results) >= k:
                    break  # K개의 결과를 넘으면 종료

        # 비동기 요약 생성
        for data_id, chunks in combined_results.items():
            full_content = " ".join(chunks)  # 결과 내용을 하나로 합침

            meta_info = metadata_index.get(data_id, {})
            link = meta_info.get('link', '')
            name = meta_info.get('name', 'Unknown')
            address = meta_info.get('address', 'Unknown')
            img = meta_info.get('img')

            if name in unique_names:
                continue  # 중복된 이름은 건너뜀
            unique_names.add(name)

            task = generate_gpt_response(name, full_content)  # GPT 요약 요청
            tasks.append(task)

            selected_results.append({
                "name": name,
                "summary": "",
                "address": address,
                "data_id": data_id,
                "image": image_url_to_base64(img),  # 이미지 URL을 base64로 변환
                "link": link
            })

        summaries = await asyncio.gather(*tasks)  # 비동기 요약 요청 실행

        for i, summary in enumerate(summaries):
            selected_results[i]['summary'] = summary  # 요약 결과를 삽입

        end_time = time.time()
        logging.info(f"전체 요약 생성 소요 시간: {end_time - start_time:.2f}초")  # 처리 시간 로그 출력

        return {
            "generated_response": "검색 결과 요약 생성 완료",  # 최종 결과 반환
            "results": selected_results
        }

    except Exception as e:
        logging.error(f"검색 중 오류 발생: {str(e)}")  # 예외 발생 시 로그 출력
        raise  # 예외 재발생

# 이미지 URL을 base64로 변환하는 함수
def image_url_to_base64(image_url):
    response = requests.get(image_url)  # 이미지 URL에 대한 HTTP 요청
    if response.status_code == 200:
        image_binary = response.content  # 이미지 바이너리 데이터 추출
        image_base64 = base64.b64encode(image_binary).decode('utf-8')  # base64로 인코딩
        return f"data:image/png;base64,{image_base64}"  # base64 이미지 문자열 반환
    else:
        raise Exception(f"Failed to retrieve image. Status code: {response.status_code}")  # 이미지 요청 실패 시 예외 발생
