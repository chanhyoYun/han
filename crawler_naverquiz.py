from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
from dotenv import load_dotenv

# dotenv에서 key값을 참조하기 때문에 dotenv를 load
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# 장고 기능을 사용하기 위한 초기 세팅
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()

from crawled_data.models import NaverQuiz, NaverQuizOption


def crawled_quiz():
    """네이버 단어 퀴즈를 크롤링하는 함수

    Returns:
        data(list): [{
                "title": "문제의 제목 부분",
                "explain": "문제 해설",
                "rate": "문제 정답률",
                "option": [
                        {
                            "content": "보기 1번",
                            "is_answer": BooleanType로 지정됨(True or False)
                        },
                        {
                            "content": "보기 2번",
                            "is_answer": BooleanType로 지정됨(True or False)
                        }, ...]
                }, ...]
    """
    # data를 담아줄 리스트 생성
    data = []

    # chromedriver 실행 파일의 경로
    chromedriver_path = "F/nbc/chromedriver_win32/chromedriver"

    # Service 객체 생성
    service = Service(chromedriver_path)

    # Chrome 드라이버 생성 및 서비스 설정
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(3)
    driver.get(
        "https://wquiz.dict.naver.com/list.dict?service=krdic&dictType=koko&sort_type=3&group_id=1"
    )
    # 기다리는 객체 생성
    wait = WebDriverWait(driver, 10)

    while True:
        open_btn = driver.find_element(By.ID, "btn_quiz_more")
        # 얼만큼 더보기를 눌러줄지는 퀴즈 더보기 옆의 숫자를 수정해주면 됨.
        # 예시 : 30만큼 더보기를 보고싶다면 퀴즈 더보기 30 / 1,746
        if open_btn.text == "퀴즈 더보기 1746 / 1,746":
            break
        open_btn.click()

    current_tab_handle = driver.current_window_handle

    # range 문의 끝에 들어가는 숫자에 따라 얼마만큼의 데이터를 크롤링 할 지 정할 수 있음.
    # 예시 : 1746개의 모든 데이터를 다 들고오고 싶다면 range(1, 1747)
    for i in range(1, 1747):
        my_problem = driver.find_element(
            By.CSS_SELECTOR, f"#content > ul.quiz_list > li:nth-child({i}) > a"
        )
        title = my_problem.find_element(By.TAG_NAME, "p").text
        new_link = my_problem.get_attribute("href")
        driver.execute_script("window.open(arguments[0]);", new_link)

        for handle in driver.window_handles:
            if handle != current_tab_handle:
                driver.switch_to.window(handle)
                driver.find_element(
                    By.XPATH, "//*[@id='answer_select_area']/a[1]"
                ).click()
                wait.until(
                    EC.visibility_of_element_located(
                        (By.XPATH, "//*[@id='quiz_answer']")
                    )
                )

                # 현재 페이지의 HTML 가져오기
                html = driver.page_source

                # html.parser로 html을 파싱하겠다고 지정
                soup = BeautifulSoup(html, "html.parser")

                # 저장할 값 지정
                explain = soup.select_one("#quiz_answer > div.answer_area > div > p")
                correct_option = soup.select_one(
                    "#quiz_answer > div.choice_result_area > ul > li.crct > span"
                )
                rate = soup.select_one(
                    "#quiz_answer > div.choice_result_area > ul > li.crct > em"
                )
                wrong_options = soup.select(
                    "#quiz_answer > div.choice_result_area > ul > li.wrong > span"
                )
                try:
                    # 딕셔너리에 순서대로 저장
                    quiz = {
                        "title": title,
                        "explain": explain.text.replace("\xa0", " "),
                        "rate": rate.text.replace("%", ""),
                        "option": [
                            {"content": correct_option.text, "is_answer": True},
                        ],
                    }

                    # 오답이 여러개일 경우, option에 순서대로 append
                    for wrong in wrong_options:
                        quiz["option"].append(
                            {"content": wrong.text, "is_answer": False}
                        )
                except:
                    # 값을 잘 가져오지 못할 때 / 오류가 발생 했을 때
                    quiz = {
                        "title": "🐛 오류 발생",
                        "explain": f"링크 확인 : {new_link}",
                        "rate": 0,
                        "option": [{"content": "", "is_answer": True}],
                    }
                    print(f"{i}번째 문제에서 오류 발생!")

                data.append(quiz)
                driver.close()
        driver.switch_to.window(driver.window_handles[0])

    return data


if __name__ == "__main__":
    quiz_data = crawled_quiz()
    for quiz in quiz_data:
        my_quiz = NaverQuiz(
            title=quiz["title"], explain=quiz["explain"], rate=quiz["rate"]
        )
        my_quiz.save()
        for option in quiz["option"]:
            quiz_option = NaverQuizOption(
                quiz=my_quiz, content=option["content"], is_answer=option["is_answer"]
            )
            quiz_option.save()
