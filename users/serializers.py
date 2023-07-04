from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import random, string
import os
from drf_extra_fields.fields import Base64ImageField

from users.models import User, Achievement, UserInfo
from users.customtoken import user_email_verify_token


def password_maker():
    """임시 비밀번호 생성기

    Returns:
        new password : 랜덤으로 영문+숫자 6개 조합의 문자열을 뱉음
    """
    random_str = string.ascii_letters + string.digits
    return "".join(random.choice(random_str) for _ in range(6))


class PasswordResetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email",)

    def update(self, instance, validated_data):
        password = password_maker()
        instance.set_password(password)
        instance.save()

        to_email = instance.email
        email = EmailMessage(
            "<한> 계정 비밀번호 초기화",
            f"변경 된 임시 비밀번호는 {password}입니다. \n\n로그인 후 반드시 회원정보에서 비밀번호를 변경해주세요.",
            to=[to_email],
        )
        email.send()
        return instance


class AchievementSerializer(serializers.ModelSerializer):
    """칭호 시리얼라이저

    칭호 생성 시리얼라이저

    """

    class Meta:
        model = Achievement
        fields = ["id", "title", "comment", "image_url"]

    def __str__(self):
        return self.title


class UserSerializer(serializers.ModelSerializer):
    """유저 시리얼라이저

    회원가입, 회원정보 수정 기능에 사용됩니다.
    """

    achieve = AchievementSerializer(many=True, required=False)
    image = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "username",
            "image",
            "wear_achievement",
            "achieve",
            "followings",
        ]

    def create(self, validated_data):
        validated_data["is_active"] = False
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        UserInfo.objects.create(player=user)
        user.save()

        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = user_email_verify_token.make_token(user)
        url = os.environ.get("FRONTEND_BASE_URL")
        to_email = user.email
        email = EmailMessage(
            f"<한> {user.username}님의 계정 인증",
            f"아래의 링크를 누르면 이메일 인증이 완료됩니다. \n\n{url}/html/activate.html?verify={uidb64}&token={token}",
            to=[to_email],
        )
        email.send()
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.image = validated_data.get("image", instance.image)
        instance.wear_achievement = validated_data.get(
            "wear_achievement", instance.wear_achievement
        )
        password = validated_data.get("password")
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserViewSerializer(serializers.ModelSerializer):
    """유저 뷰 시리얼라이저

    유저 보기전용 시리얼라이저

    """

    achieve = AchievementSerializer(many=True, required=False)
    followings = UserSerializer(many=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "username",
            "image",
            "wear_achievement",
            "achieve",
            "followings",
        ]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["username"] = user.username
        return token


class RankingSerializer(serializers.ModelSerializer):
    player = UserSerializer()

    class Meta:
        model = UserInfo
        fields = ["player", "level", "experiment", "battlepoint"]


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = "__all__"


class UserBattleFriendSerializer(UserSerializer):
    followings = serializers.SerializerMethodField()
    user_info = UserInfoSerializer(source="player.first", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "image",
            "wear_achievement",
            "achieve",
            "followings",
            "user_info",
        ]

    def get_followings(self, obj):
        followings = obj.followings.values_list("username", "email")
        return {
            str(i): {"username": username, "email": email}
            for i, (username, email) in enumerate(followings)
        }
