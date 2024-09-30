import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# API 키 및 자격 증명 로드
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
