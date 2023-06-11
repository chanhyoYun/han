from django.urls import reverse
from rest_framework.test import APITestCase
from users.models import User, Achievement


"""테스트 요약

총 6개 테스트
1. 회원가입

2. 회원정보 조회
3. 회원정보 수정
4. 회원탈퇴

5. 토큰 로그인
6. 토큰 리프레쉬
"""


class UserBaseTestCase(APITestCase):
    """유저기능 테스트 셋업

    유저기능 테스트 셋업입니다.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user_signup_data = {
            "username": "signupuser",
            "password": "qhdks111!",
            "email": "signupuser@gmail.com",
        }
        cls.set_up_user = User.objects.create_user(
            email="testuser@gmail.com",
            password="qhdks111!",
        )
        cls.user_edit_data = {"username": "testuser"}
        cls.user_login_data = {"email": "testuser@gmail.com", "password": "qhdks111!"}

    def setUp(self) -> None:
        login_user = self.client.post(reverse("login"), self.user_login_data).data
        self.access = login_user["access"]
        self.refresh = login_user["refresh"]


class UserSignUpTestCase(UserBaseTestCase):
    """유저 회원가입 테스트

    Userview에 회원가입(get) 기능을 테스트합니다.
    """

    def test_signup(self):
        """1. 회원가입

        회원가입 정상동작 테스트입니다.
        스테이터스 코드, 결과 메세지, DB값을 검사합니다.
        """
        url = reverse("signup")
        data = self.user_signup_data
        response = self.client.post(
            path=url,
            data=data,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {"message": "가입완료"})

        self.assertTrue(User.objects.get(email=data["email"]))


class UserDetailTestCase(UserBaseTestCase):
    """유저 상세기능 테스트

    UserDetailView에 회원정보조회(get), 회원정보수정(patch), 회원탈퇴(delete) 기능을 테스트합니다.
    """

    def test_userinfo_get(self):
        """2. 회원정보조회

        회원정보조회 정상동작 테스트입니다.
        스테이터스 코드, 결과 여부를 검사합니다.
        """
        url = reverse("users_id", kwargs={"user_id": self.set_up_user.id})
        response = self.client.get(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)

    def test_userinfo_patch(self):
        """3. 회원정보수정

        회원정보수정 정상동작 테스트입니다.
        스테이터스 코드, 결과 메세지, DB값을 검사합니다.
        """
        url = reverse("users_id", kwargs={"user_id": self.set_up_user.id})
        data = self.user_edit_data
        response = self.client.patch(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access}",
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "수정완료"})

        test_edited_user = User.objects.get(id=self.set_up_user.id)
        self.assertEqual(test_edited_user.username, data["username"])

    def test_signout(self):
        """4. 회원탈퇴

        회원탈퇴 정상동작 테스트입니다.
        스테이터스 코드, 결과 메세지, DB값을 검사합니다.
        """
        url = reverse("users_id", kwargs={"user_id": self.set_up_user.id})
        response = self.client.delete(
            path=url,
            HTTP_AUTHORIZATION=f"Bearer {self.access}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "탈퇴완료"})

        test_signouted_user = User.objects.get(id=self.set_up_user.id)
        self.assertEqual(test_signouted_user.is_active, False)


class UserTokenTestCase(UserBaseTestCase):
    """토큰 로그인 및 갱신 테스트

    CustomTokenObtainPairView, TokenRefreshView의
    토큰 로그인 기능, 토큰 리프레쉬 기능을 테스트합니다.
    """

    def test_login(self):
        """5. 토큰 로그인

        토큰 로그인 정상동작 테스트입니다.
        스테이터스 코드, 결과 여부를 검사합니다.
        """
        url = reverse("login")
        data = self.user_login_data
        response = self.client.post(
            path=url,
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)

    def test_token_refresh(self):
        """6. 토큰 리프레쉬

        토큰 리프레쉬 정상동작 테스트입니다.
        스테이터스 코드, 결과 여부를 검사합니다.
        """
        url = reverse("token_refresh")
        data = {"refresh": self.refresh}
        response = self.client.post(
            path=url,
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)
