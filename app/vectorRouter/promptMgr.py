from dotenv import load_dotenv
from app.config import OPENAI_API_KEY
from openai import OpenAI

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)

# 프롬프트 생성 함수
def generate_gpt_response(name: str, full_content: str):
    """
    OpenAI를 통해 요약된 정보를 반환하는 함수.
    중복된 정보 없이 새로운 정보를 생성하는 것을 목표로 함.
    """
    try:
        # OpenAI ChatCompletion 호출 (새로운 API 사용)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    "당신은 한국의 맛집 전문가입니다. "
                    "사용자가 입력한 문장이나 단어를 바탕으로 맛집을 찾아주는 것이 목표입니다."
                    "요약은 사용자가 가게를 빠르게 이해할 수 있도록 간결하고 명확해야 합니다."
                    "존댓말을 써서 예의바르고 친절한 말투로 답변해주세요."
                )},
                {"role": "user", "content": f"""
                가게 이름: {name}\n
                가게 설명: {full_content}\n
                아래 항목을 기준으로 요약을 작성하세요:\n
                대표 메뉴: 가게의 인기 메뉴를 강조하세요.\n
                분위기: 가게의 분위기를 간결하게 설명하세요 (예: 로맨틱한, 캐주얼한, 가족 친화적인 등).\n
                차별점: 이 가게만의 특별한 특징을 강조하세요.\n
                최대 300자로 요약을 간결하게 작성하세요.
                문장이 끝나면 그에 맞게 다음 줄로 이동해서 작성해주세요.
                사용자가 짧은 검색어를 입력했다면 키워드에 맞는 링크와 요약을 작성해주세요.
                식당에 대한 평가나 생각을 중심으로 요약해주세요."""}
            ],
            temperature=0.7,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0.5,  # 중복된 내용에 대한 패널티
            presence_penalty=0.5    # 새로운 정보에 대한 장려
        )

        # API로부터 받은 응답
        result = response.choices[0].message.content

        # 강조 표현을 없애고 각 항목을 새로운 줄로 이동시킴
        formatted_result = result.replace("**", "")  # 강조 표시 제거
        # HTML에서 줄바꿈을 반영하기 위해 '\n'을 '<br>'로 변환
        formatted_result = formatted_result.replace("\n", "<br>")

        # 항목을 줄바꿈 처리
        formatted_result = formatted_result.replace("대표 메뉴:", "\n대표 메뉴:")\
                                           .replace("분위기:", "\n분위기:")\
                                           .replace("차별점:", "\n차별점:")


        return formatted_result

    except Exception as e:
        print(f"OpenAI API 오류 발생: {str(e)}")
        return "요약 생성 실패"
