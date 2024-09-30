from DBMgr.connetion import create_connection
from DBMgr.summarizer import summarize_reviews
from models import SearchResult

def saveToRDB(data: SearchResult):
    """
    MySQL DB에 데이터를 저장하고 생성된 PK를 반환하는 함수
    """
    connection = create_connection()

    try:
        with connection.cursor() as cursor:
            # 리뷰를 요약
            summary = summarize_reviews(data.title, data.reviews)

            # 데이터 삽입 SQL 쿼리
            sql = """
            INSERT INTO restaurant 
            (title, description, adr_address, international_phone_number)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data.title, summary, data.address, data.international_phone_number
            ))
            connection.commit()
            return cursor.lastrowid

    except Exception as e:
        print(f"데이터베이스 저장 중 오류 발생: {e}")
        return None

    finally:
        connection.close()

