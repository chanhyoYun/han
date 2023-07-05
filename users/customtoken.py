from rest_framework_simplejwt.tokens import Token, AccessToken, RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class CustomToken(Token):
    """JWT 커스텀 토큰

    for_user 메소드를 커스텀하여
    CustomAccessToken과 CustomRefreshToken에서 for_user 호출 시
    이메일과 유저네임을 포함하여 토큰을 제공합니다.
    소셜 로그인 완료처리에서 사용됩니다.
    """

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

    일반 유저 이메일 인증 시 판별에 사용하는 토큰
    """

    def _make_hash_value(self, user, timestamp):
        """일반 유저 정보 해싱

        PasswordResetTokenGenerator의 _make_hash_value method를 오버라이딩

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
