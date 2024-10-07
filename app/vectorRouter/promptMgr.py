from dotenv import load_dotenv
from app.config import OPENAI_API_KEY
from langchain.schema import Document  
from openai import OpenAI

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)

# 프롬프트
def summarize_desc(name: str, naver_description, reviews):
    """
    가게 이름과 설명을 바탕으로 OpenAI를 통해 요약된 정보를 반환하는 함수.
    중복된 정보 없이 새로운 정보를 생성하는 것을 목표로 함.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "아래의 맛집 정보를 요약해서 가게의 특징을 잘 알수있게해. 너무 길게는 하지말고, 그냥 적당히200자 내외로, 중복된 정보 없게요약해."},
                {"role": "user", "content": f"""가게 이름: {name}
                가게 설명: {naver_description}
                가게 리뷰: {reviews}"""}
            ],
            temperature=0.7,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0.5,  # 중복된 내용에 대한 패널티
            presence_penalty=0.5    # 새로운 정보에 대한 장려
        )
        result = response.choices[0].message.content
        print("요약결과"+result)
        print("desc"+naver_description)
        return result

    except Exception as e:
        print(f"OpenAI API 오류 발생: {e}")
        return "요약 생성 실패"