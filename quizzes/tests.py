from django.urls import reverse
from rest_framework.test import APITestCase
from users.models import User
from quizzes.models import Quiz, Option, QuizReport


"""테스트 요약

총 3개 테스트
1. 퀴즈 불러오기
2. 퀴즈 제안하기

3. 퀴즈 신고하기
"""


class QuizBaseTestCase(APITestCase):
    """퀴즈기능 테스트 셋업

    퀴즈기능 테스트 셋업입니다.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.set_up_user = User.objects.create_user(
            email="testuser@gmail.com",
            password="qhdks111!",
        )
        cls.user_login_data = {"email": "testuser@gmail.com", "password": "qhdks111!"}

        cls.quiz_suggest_data = {
            "quiz": {"title": "유형", "content": "내용", "explain": "해설", "difficulty": 1},
            "options": [
                {"content": "1번보기", "is_answer": False},
                {"content": "2번보기", "is_answer": True},
            ],
        }
        cls.set_up_quizzes = [Quiz.objects.create(difficulty=1) for x in range(10)]
        cls.quiz_report_data = {"content": "신고내용"}

    def setUp(self) -> None:
        login_user = self.client.post(reverse("login"), self.user_login_data).data
        self.access = login_user["access"]
        self.refresh = login_user["refresh"]


class QuizTestCase(QuizBaseTestCase):
    """퀴즈 제안하기, 불러오기 테스트

    QuizView에 퀴즈 불러오기(get), 퀴즈 제안하기(post) 기능을 테스트합니다.
    """

    def test_quiz_get(self):
        """1. 퀴즈 불러오기

        퀴즈 불러오기 정상동작 테스트입니다.
        스테이터스 코드, 결과값이 10개인지 검사합니다.
        """
        url = reverse("quiz")
        response = self.client.get(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(self.set_up_quizzes))

    def test_quiz_post(self):
        """2. 퀴즈 제안하기

        퀴즈 제안하기 정상동작 테스트입니다.
        스테이터스 코드, 결과 메세지, DB값을 검사합니다.
        """
        url = reverse("quiz")
        data = self.quiz_suggest_data
        response = self.client.post(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access}",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {"message": "제출완료"})

        self.assertTrue(Quiz.objects.get(title=data["quiz"]["title"]))
        self.assertTrue(Option.objects.get(content=data["options"][0]["content"]))


class QuizReportTestCase(QuizBaseTestCase):
    """퀴즈 신고하기 테스트

    QuizReportView에 퀴즈 신고하기(post) 기능을 테스트합니다.
    """

    def test_quiz_report(self):
        """3. 퀴즈 신고하기

        퀴즈 신고하기 정상동작 테스트입니다.
        스테이터스 코드, 결과메세지, DB값을 검사합니다.
        """
        url = reverse("quiz_report", kwargs={"quiz_id": self.set_up_quizzes[0].id})
        data = self.quiz_report_data
        response = self.client.post(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access}",
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "신고완료"})

        self.assertTrue(QuizReport.objects.get(content=data["content"]))
