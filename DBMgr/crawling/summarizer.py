# summarizer.py

import openai
from dotenv import load_dotenv
from langchain.schema import Document  

from datas.config import OPENAI_API_KEY
load_dotenv()
# OpenAI API 키 설정

openai.api_key = OPENAI_API_KEY

def summarize_desc(name: str, desc):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "아래의 요청에따라 가게의 특징을 잘 알 수 있게 최대 100자 이내로 요약해주세요. (예: 우유푸딩이 맛있는 중세시대 느낌의 조용한 까페입니다. 대표메뉴로는 아메리카노, 티라미수케익 등이 있습니다. 데이트코스로도 적합합니다.)"},
                {"role": "user", "content": f"가게 이름: {name}\n설명: {name}\n\n가게의 인기 메뉴, 음식점 분류 (예 : 한식집, 일식집), 가게의 분위기를 바탕으로 100자 이내로 요약해줘."}],
            temperature=0.7,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        result = response.choices[0].message.content
        print(result)
        return result

    except openai.error.OpenAIError as e:
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