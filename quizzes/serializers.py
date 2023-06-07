from rest_framework import serializers
from quizzes.models import Quiz, Option


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = "__all__"


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = "__all__"

    def __init__(self, instance=None, data=..., **kwargs):
        quiz_id = kwargs.pop("quiz_id")
        for option in data:
            option["quiz"] = quiz_id
        super().__init__(instance, data, **kwargs)
