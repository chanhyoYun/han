import requests
from bs4 import BeautifulSoup
import json
import os

# 현재 파일의 부모 디렉토리 찾기
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# HTTP 링크 가져오기
req = requests.get(
    "https://wquiz.dict.naver.com/result.dict?service=krdic&dictType=koko&quizId=76df29342b404ba59a3aa8cc8f68517e&answerId=6d41c71fcc2941189a8645d47fac483b&group_id=1&seq=0"
)

# html 지정
html = req.text

# html.parser로 html을 파싱하겠다고 지정
soup = BeautifulSoup(html, "html.parser")

# 위치 지정
explain = soup.select_one("#quiz_answer > div.answer_area > div > p")
correct_option = soup.select_one(
    "#quiz_answer > div.choice_result_area > ul > li.crct > span"
)
wrong_options = soup.select(
    "#quiz_answer > div.choice_result_area > ul > li.wrong > span"
)

data = {
    "explain": explain.text,
    "option": [
        {"content": correct_option.text, "is_answer": 1},
    ],
}


for wrong in wrong_options:
    data["option"].append({"content": wrong.text, "is_answer": 0})

with open(os.path.join(BASE_DIR, "result.json"), "w+", encoding="utf-8") as json_file:
    json.dump(data, json_file, ensure_ascii=False)
