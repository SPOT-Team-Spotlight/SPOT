# 크롤링 상수
TEST_MODE = "테스트 모드"
GATHER_MODE = "데이터 수집 모드"

"""
전처리 상수
"""
# 임베딩
EMBEDDING_MODEL_TYPES = [
    "OpenAI"
]

EMBEDDING_MODEL_VERSIONS = {
    "OpenAI": ["text-embedding-3-small"]
    # "OpenAI": ["text-embedding-3-small", "text-embedding-3-large"],
    # "Hugging Face": ["bert-base-uncased", "roberta-base"],
    # "Custom": ["custom-model-v1", "custom-model-v2"]
}

# 벡터 db
VECTOR_DBS = [
    "Faiss"
]

# 요약 모델
SUMMARY_MODEL_TYPES = [
    "OpenAI"
]

SUMMARY_MODEL_VERSIONS = {
    "OpenAI": ["gpt-3.5-turbo", "gpt-4o-mini"]
}