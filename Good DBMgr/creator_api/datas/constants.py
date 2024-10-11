# 크롤링 상수
TEST_MODE = "테스트 모드(20)"
GATHER_MODE = "데이터 수집 모드(60)"

"""
전처리 상수
"""
# 임베딩
EMBEDDING_MODEL_TYPES = [
    "OpenAI"
]

EMBEDDING_MODEL_VERSIONS = {
    "OpenAI": ["text-embedding-3-small"]
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