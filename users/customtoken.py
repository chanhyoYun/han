from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework_simplejwt.tokens import Token, AccessToken, RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class CustomToken(Token):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token["email"] = user.email
        token["username"] = user.username
        return token


class CustomAccessToken(CustomToken, AccessToken):
    pass


class CustomRefreshToken(CustomToken, RefreshToken):
    pass


class UserEmailVerifyToken(PasswordResetTokenGenerator):
    """일반 유저 이메일 인증 토큰

    일반 유저 이메일 인증 시 해당 토큰의 정보로 판별하게 한다.
    """

    def _make_hash_value(self, user, timestamp):
        """일반 유저 정보 해싱

        PasswordResetTokenGenerator의 _make_hash_value method를 오버라이딩.

        Args:
            user : 유저 모델의 인스턴스 객체
            timestamp : 토큰 생성 시간

        Returns:
            user.pk : 유저의 고유 id 값
            timestamp : 토큰 생성 시간
            user.is_active : 유저의 active 여부
        """
        return user.pk + timestamp + user.is_active


user_email_verify_token = UserEmailVerifyToken()
