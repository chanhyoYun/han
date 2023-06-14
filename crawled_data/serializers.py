from rest_framework import serializers
from crawled_data.models import *


class NaverQuizOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NaverQuizOption
        fields = (
            "content",
            "is_answer",
        )


class KrDictExplainSerializer(serializers.ModelSerializer):
    class Meta:
        model = KrDictQuizExplain
        fields = ("content",)


class KrDictExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = KrDictQuizExample
        fields = (
            "word_type",
            "content",
        )


class NaverQuizSerializer(serializers.ModelSerializer):
    options = NaverQuizOptionSerializer(many=True)

    class Meta:
        model = NaverQuiz
        fields = "__all__"


class KrDictQuizSerializer(serializers.ModelSerializer):
    explains = KrDictExplainSerializer(many=True)
    examples = KrDictExampleSerializer(many=True)

    class Meta:
        model = KrDictQuiz
        fields = "__all__"
