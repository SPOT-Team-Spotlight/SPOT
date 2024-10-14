## How to use 
내부적으로 naver API와 구글 API를 사용하고 있다
.env 파일로 해당 키를 관리하고 있고 해당 파일은 .gitignroe로 git에는 올라가지 않으니
하는 사람이 추가로 만들어서 할당해야 함

- 라이브러리 미설치시 아래 코드 터미널에 작성하기
-> requirements.txt 파일에 필요한 패키지 설치
  - pip install -r requirements.txt

- 실행시 터미널 입력
  - conda activate {가상환경이름}
  - uvicorn app.main:app --reload 입력

- vdb 초기화 방법
삭제 : spot_index.bin, spot_metadata.pkl, vdbLog.txt, log_number.txt
- 새로 크롤링 하실 때, vdb_data의 last_id.json 날려주세요

<Good DBMgr 실행법>
- 실행 위치 바꾸기
예) cd "C:/Users/201-17/Documents/GitHub/SPOT/Good DBMgr"

- 실행 코드
python -m good_main

< 모바일 실행 환경법 >
1. 와이파이 연결 
2. 유비콘 실행시 uvicorn app.main:app --reload --host=0.0.0.0 하면 모바일에서 열수있음
3. 모바일주소 = > 터미널에서 ipconfig 입력해서 IPv4 Address에있는 숫자들 입력 후 :8000 