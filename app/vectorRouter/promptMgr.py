# promptMgr.py
import aiohttp
import os
from dotenv import load_dotenv

# .env 파일에서 API 키 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 비동기 OpenAI GPT 요약 생성 함수
async def generate_gpt_response(name: str, full_content: str):
    """
    OpenAI를 통해 요약된 정보를 비동기적으로 반환하는 함수.
    중복된 정보 없이 새로운 정보를 생성하는 것을 목표로 함.
    """
    try:
        # OpenAI API 호출을 위한 헤더 및 요청 데이터 구성
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                    {
                        "role": "system",
                        "content": """
                        
                        # Task
                        - 사용자가 가게를 빠르게 이해할 수 있도록 간결하고 명확해야 합니다.
                        - output format 형태를 지켜주세요.
                        - output format의 내용은 존댓말을 써서 예의 바르고 친절한 말투로 답변해주세요.
                        """
                    },
                        {
                            "role": "user",
                            "content": f"""
                            가게 이름: {name}
                            가게 설명: {full_content}
                    대표 메뉴: 가게의 인기 메뉴를 강조하세요.\n
                    분위기: 가게의 분위기를 간결하게 설명하세요 (예: 로맨틱한, 캐주얼한, 가족 친화적인 등).\n
                    차별점: 이 가게만의 특별한 특징을 강조하세요.\n
                    
                    # Output Format
                    {{
                        "대표메뉴": "",
                        "분위기": "",
                        "차별점": ""
                    }}
                    """
                        }
            ],

            "temperature": 0.1,
            "max_tokens": 200,
            "top_p": 1,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.5,
        }

        # 비동기 HTTP 요청을 보냄
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers) as response:
                if response.status == 200:
                    result_json = await response.json()
                    result = result_json['choices'][0]['message']['content']

                    # 강조 표시 제거 및 포맷팅
                    formatted_result = result.replace("**", "")  # 강조 표시 제거
                    formatted_result = formatted_result.replace("{", "")  # 중괄호 제거
                    formatted_result = formatted_result.replace("}", "")  # 중괄호 제거
                    formatted_result = formatted_result.replace(",", "")  # 쉼표 제거
                    formatted_result = formatted_result.replace("\n", "<br>")

                    # 항목별로 줄바꿈 처리
                    formatted_result = formatted_result.replace("대표 메뉴:", "\n대표 메뉴:")\
                                                       .replace("분위기:", "\n분위기:")\
                                                       .replace("차별점:", "\n차별점:")
                    
                    return formatted_result
                else:
                    return f"요약 생성 실패: {response.status}"

    except Exception as e:
        print(f"OpenAI API 오류 발생: {str(e)}")
        return "요약 생성 실패"