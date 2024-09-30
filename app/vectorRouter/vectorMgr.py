import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings  # 새로운 모듈에서 임포트
import numpy as np

# .env 파일에서 API 키 로드 (환경 변수 설정)
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 임베딩 객체 생성
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-3-small")

# 텍스트 임베딩 함수
def get_openai_embedding(text): 
    """
    OpenAI를 통해 자연어 임베딩을 생성하는 함수
    :param text: 임베딩 할 텍스트
    :return: 임베딩 벡터
    """
    embedding = embeddings.embed_query(text)
    return np.array(embedding, dtype=np.float32)