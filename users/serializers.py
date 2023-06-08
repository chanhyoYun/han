from rest_framework import serializers
from users.models import User, Achievement
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ["id", "title", "comment"]

    def __str__(self):
        return self.title


class UserSerializer(serializers.ModelSerializer):
    achieve = AchievementSerializer(many=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "username",
            "image",
            "experiment",
            "level",
            "day",
            "wear_achievement",
            "achieve",
        ]

    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.image = validated_data.get("image", instance.image)
        instance.wear_achievement = validated_data.get(
            "wear_achievement", instance.wear_achievement
        )
        instance.save()
        return instance
