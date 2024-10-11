# 저장하면 로그를 남기는 코드
from datetime import datetime
import os

# 로그 번호를 저장할 파일 경로
log_number_file = 'log_number.txt'

# 마지막 로그 번호를 저장하는 함수
def save_log_number(number):
    with open(log_number_file, 'w') as file:
        file.write(str(number))

# 마지막 로그 번호를 불러오는 함수
def load_log_number():
    if not os.path.exists(log_number_file):
        return 0  # 파일이 없으면 0부터 시작
    with open(log_number_file, 'r') as file:
        return int(file.read().strip())

def write_log(region, keyword, start_count, save_count):
    # 파일에 쓸 딕셔너리 데이터
    data = {
        'region': region,
        'keyword': keyword,
        'count': save_count
    }

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # TXT 파일 열기 (쓰기 모드)
    with open('vdbLog.txt', 'a', encoding='utf-8') as file:
        for key, value in data.items():
            file.write(f'{key}: {value}\n')
        else:
            num = start_count+save_count
            file.write(f'[저장 시간 : {current_time}, 저장된 개수 : {num}개]\n')    

    print(f"{data} 저장되었습니다.")
    return save_count

def vdb_logging(region, keyword, count):
    """
    크롤링을 한 결과를 저장하는 함수
    """
    log_number = load_log_number()
    count = write_log(region, keyword, log_number, count)
    log_number += count
    save_log_number(log_number)


