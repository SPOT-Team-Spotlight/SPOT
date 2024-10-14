import os

# 프로젝트 루트 디렉토리 찾기
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# vdb_data 디렉토리 경로 (현재 파일의 디렉토리)
VDB_DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# last_id.json 파일 경로
ID_FILE_PATH = os.path.join(VDB_DATA_DIR, "last_id.json")

# 기타 공통으로 사용할 상수들을 따로 빼서 저장하자