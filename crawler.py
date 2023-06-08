from bs4 import BeautifulSoup
import json
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# data를 담아줄 dict 생성
data = {}

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
for i in range(1, 21):
    my_problem = driver.find_element(
        By.CSS_SELECTOR, f"#content > ul.quiz_list > li:nth-child({i}) > a"
    )
    title = my_problem.find_element(By.TAG_NAME, "p").text
    new_link = my_problem.get_attribute("href")
    driver.execute_script("window.open(arguments[0]);", new_link)

    for handle in driver.window_handles:
        if handle != current_tab_handle:
            driver.switch_to.window(handle)
            driver.find_element(By.XPATH, "//*[@id='answer_select_area']/a[1]").click()
            element = wait.until(
                EC.visibility_of_element_located((By.XPATH, "//*[@id='quiz_answer']"))
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

            # 딕셔너리에 순서대로 저장
            problem = {
                "title": title,
                "explain": explain.text.replace("\xa0", " "),
                "rate": rate.text.replace("%", ""),
                "option": [
                    {"content": correct_option.text, "is_answer": 1},
                ],
            }

            # 오답이 여러개일 경우, option에 순서대로 append
            for wrong in wrong_options:
                problem["option"].append({"content": wrong.text, "is_answer": 0})

            # data라는 딕셔너리에 담아주기
            data[i] = problem
            driver.close()
    driver.switch_to.window(driver.window_handles[0])

# json 데이터 저장
with open(os.path.join(BASE_DIR, "result.json"), "w+", encoding="utf-8") as json_file:
    json.dump(data, json_file, ensure_ascii=False)
