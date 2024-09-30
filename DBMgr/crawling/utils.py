import re

# HTML 태그를 정규식으로 제거하는 함수
def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def clean_word(raw_word):
    """
    string안에 특정 문자를 제거하는 함수
    :param raw_word: 특정 문자를 제거할 대상 문자열('<' , ',' 제거됨)
    """
    # 쉼표를 공백으로 대체
    cleaned_string = raw_word.replace('>', ' ')
    cleaned_string = cleaned_string.replace(',', ' ')
    
    return cleaned_string

