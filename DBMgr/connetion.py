import pymysql

#   여기서 rdb 연결 관리합니다.
def create_spot():
    """
    MySQL 데이터베이스가 없을 경우 생성하는 함수
    """
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='@rlawlgid121',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS spot")
            connection.commit()
            print("Db생성 완료")
    except Exception as e:
        print(f"데이터베이스 생성 중 오류 발생: {e}")
    finally:
        connection.close()


def create_table(connection):
    """
    MySQL 데이터베이스에 테이블이 없을 경우 생성하는 함수
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS restaurant (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255),
                description TEXT,
                adr_address VARCHAR(255),
                international_phone_number VARCHAR(20)
            )
            """)
            connection.commit()
            print("Table 'restaurant'가 성공적으로 생성되었거나 이미 존재합니다.")
    except Exception as e:
        print(f"테이블 생성 중 오류 발생: {e}")

def create_user_table(connection):

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
            """)
            connection.commit()
            print("유저등록 성공 ㅋ ㅅㅅ")
    except Exception as e:
        print(f"테이블 생성 중 오류 발생: {e}")

def create_connection():
    create_spot()
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='@rlawlgid121',
        database='spot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    # 테이블 생성
    create_table(connection)
    #create_user_table(connection)
    return connection

