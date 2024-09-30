from dotenv import load_dotenv
from app.config import OPENAI_API_KEY
from langchain.schema import Document  
from openai import OpenAI

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)

# 프롬프트
def summarize_desc(name: str, desc):
    """
    가게 이름과 설명을 바탕으로 OpenAI를 통해 요약된 정보를 반환하는 함수.
    중복된 정보 없이 새로운 정보를 생성하는 것을 목표로 함.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 맛집 전문가입니다. 사용자가 입력한 검색어에 맞는 맛집을 추천해주세요."},
                {"role": "user", "content": f"가게 이름: {name}\n설명: {name}\n\n가게의 인기 메뉴, 음식점 분류 (예 : 한식집, 일식집), 가게의 분위기를 바탕으로 100자 이내로 중복되지 않게 요약해주세요. 이미 언급된 정보는 반복하지 말고, 최대한 새로운 정보를 제공해주세요."}
            ],
            temperature=0.7,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0.5,  # 중복된 내용에 대한 패널티
            presence_penalty=0.5    # 새로운 정보에 대한 장려
        )
        result = response.choices[0].message.content
        return result

    except Exception as e:
        print(f"OpenAI API 오류 발생: {e}")
        return "요약 생성 실패"