from rest_framework_simplejwt.tokens import Token, AccessToken, RefreshToken


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
