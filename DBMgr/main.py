"""
웹 크롤링을 통해서 Faiss DB를 만드는 프로그램
"""
# API 키를 환경변수로 관리하기 위한 설정 파일
from dotenv import load_dotenv
from vectorMgr import saveToVDB, searchVDB
from crawling.crawling import start_crawling, make_datas
from logger import vdb_logging
from tools.metaMgr import print_meta

user_input = int()

# API 키 정보 로드
load_dotenv()

def find(region : str = "데이터 크롤링 할 지역",
         keyword : str = "크롤링 할 단어"):
    """
    정보를 찾고, 데이터를 만들어서 반환해주는 함수
    """
    infos = start_crawling(keyword=keyword, region=region)
    infos = make_datas(infos)

    return infos

def save(datas : list = "SearchResult list를 주면 DB에 저장하는 함수"):
    """
    크롤링한 데이터를 저장하는 함수
    """
    for data in datas: 
        saveToVDB(data=data)

def interface():
    """
    간단 인터페이스
    """
    message = """
        DB 형성 프로그램\n
        숫자를 입력하시면 해당 행동을 실행합니다 
        1 : db 형성
        2 : db 조회
        3 : meta 데이터 출력
        0 : 종료
        """
    print(message)    

if __name__ == "__main__":
    user_input = str()

    while user_input != '0':
        interface()

        user_input = input("입력해 주세요: ")

        if user_input == '1':
            print("==DB생성==")
            region = input("지역을 입력해 주세요: ")
            keyword = input("키워드를 입력해 주세요: ")
            print(f"region:{region},keyword:{keyword}로 크롤링 중입니다... 잠시 기다려 주세요.") 
           
            result = find(keyword=keyword, region=region)
            print(f"검색 완료! DB 생성중입니다...") 
            save(result)
            vdb_logging(region=region, keyword=keyword, count=len(result))
            
        elif user_input == '2':
            print("==DB조회==")
            keyword = input("키워드를 입력해 주세요: ")
            search_amount = input("가져올 개수를 입력해 주세요: ")
            print(f"keyword:{keyword}를 DB에서 검색 중입니다... 잠시 기다려 주세요.") 
            result = searchVDB(query=keyword, search_amount=int(search_amount))
            
            print(f"검색된 결과 {len(result)}개 입니다.")
            count = 1
            print(count, ":", result[0])


            more = input("더보기 y, 그만 보기 n : ")

            if(more == 'y'):
                for i in range(1, len(result)):
                    count +=1
                    print(count, ":", result[i])
        elif user_input == '3':
            print("==메타데이터를 출력합니다==")
            print_meta()

        elif user_input == '0':
            print("종료합니다")

    



