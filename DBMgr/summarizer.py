
import openai
from dotenv import load_dotenv

from config import OPENAI_API_KEY
load_dotenv()
# OpenAI API 키 설정
openai.api_key = OPENAI_API_KEY

def summarize_reviews(restaurant_name: str, reviews: list):
    # 리뷰 텍스트들을 하나로 연결함
    reviews_text = " ".join([review.get('text', '') for review in reviews])

    print("리뷰요약="+reviews_text)
    print("가게이름 잘 가져오나 확인"+restaurant_name)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "아래의 요청에따라 가게의 특징을 잘 알 수 있게 100자 이내로 요약해. (예: 우유푸딩이 맛있는 중세시대 느낌의 조용한 까페입니다. 대표메뉴로는 아메리카노, 티라미수케익 등이 있습니다. 데이트코스로도 적합합니다.)"},
                {"role": "user", "content": f"가게 이름: {restaurant_name}\n리뷰: {reviews_text}\n\n가게의 인기 메뉴, 음식점 분류 (예 : 한식집, 일식집), 가게의 분위기를 바탕으로 100자 이내로 요약해줘."}],
            temperature=0.7,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        summary = response.choices[0].message.content
        print("gpt프롬프트=" + summary)
        return summary

    except openai.error.OpenAIError as e:
        print(f"OpenAI API 오류 발생: {e}")
        return "요약 생성 실패"
