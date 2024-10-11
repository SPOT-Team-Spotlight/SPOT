# summarizer.py
from dotenv import load_dotenv
from .datas.config import OPENAI_API_KEY
from langchain.schema import Document  
from openai import OpenAI

load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)

def summarize_desc(name: str, desc):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "아래의 요청에따라 가게의 특징을 잘 알 수 있게 요약해주세요. (예: 우유푸딩이 맛있는 중세시대 느낌의 조용한 까페입니다. 대표메뉴로는 아메리카노, 티라미수케익 등이 있습니다. 데이트코스로도 적합합니다.)"},
                {"role": "user", "content": f"가게 이름: {name}\n설명: {desc}\n\n"}
            ],
            temperature=0.7,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        result = response.choices[0].message.content
        return result

    except Exception as e:
        print(f"OpenAI API 오류 발생: {e}")
        return "요약 생성 실패"

def do_summarize(name: str, descs: list):
    """
    일단 모든 청킹 단위를 요약해서 돌려주는 메서드
    나중에는 더 줄이는 메커니즘을 생각해보자
    """
    result = str()

    for desc in descs:
        result = result + summarize_desc(name, desc)

    return result