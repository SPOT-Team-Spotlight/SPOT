- How to use - 
내부적으로 naver API와 구글 API를 사용하고 있다
.env 파일로 해당 키를 관리하고 있고 해당 파일은 .gitignroe로 git에는 올라가지 않으니
하는 사람이 추가로 만들어서 할당해야 함

- 라이브러리 미설치시 아래 코드 터미널에 작성하기
-> requirements.txt 파일에 필요한 패키지 설치
pip install -r requirements.txt

- 실행시 터미널 입력
conda activate {가상환경이름}
uvicorn app.main:app --reload