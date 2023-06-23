from rest_framework import serializers
from crawled_data.models import *
import random


class NaverQuizOptionSerializer(serializers.ModelSerializer):
    """네이버 알쏭달쏭 퀴즈 옵션 시리얼라이저

    네이버 알쏭달쏭 퀴즈의 옵션들을 처리할 때 사용합니다.
    """

    class Meta:
        model = NaverQuizOption
        fields = (
            "content",
            "is_answer",
        )


class KrDictExplainSerializer(serializers.ModelSerializer):
    """한국어 기초 사전 설명 시리얼라이저

    한국어 기초 사전의 설명들을 처리할 때 사용합니다.
    """

    class Meta:
        model = KrDictQuizExplain
        fields = ("content",)


class KrDictExampleSerializer(serializers.ModelSerializer):
    """한국어 기초 사전 에시 시리얼라이저

    한국어 기초 사전의 예시들을 처리할 때 사용합니다.
    """

    class Meta:
        model = KrDictQuizExample
        fields = (
            "word_type",
            "content",
        )


class NaverQuizSerializer(serializers.ModelSerializer):
    """네이버 알쏭달쏭 퀴즈 시리얼라이저

    네이버 알쏭달쏭 퀴즈를 처리할 때 사용합니다.
    옵션은 NaverQuizOptionSerializer를 통해 처리합니다.
    """

    options = NaverQuizOptionSerializer(many=True)

    class Meta:
        model = NaverQuiz
        fields = "__all__"


class KrDictSerializer(serializers.ModelSerializer):
    """한국어 기초 사전 시리얼라이저

    한국어 기초 사전 모델을 처리할 때 사용합니다.
    예시는 KrDictExampleSerializer를 통해 처리합니다.
    """

    examples = KrDictExampleSerializer(many=True)

    class Meta:
        model = KrDictQuiz
        fields = "__all__"


class FillInTheBlankSerializer(serializers.ModelSerializer):
    dict_word = KrDictSerializer()

    class Meta:
        model = KrDictQuizExplain
        fields = [
            "dict_word",
            "content",
        ]


class MeaningSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        # 틀린 답 개수
        _wrong_word_value = 4

        representation = super().to_representation(instance)

        # 설명 덧붙이기
        explains = KrDictQuizExplain.objects.filter(dict_word=instance.pk)

        representation["explains"] = list()
        for explain in explains:
            representation["explains"].append(
                {
                    "content": explain.content,
                }
            )

        # 틀린 단어 넣기
        all_words_count = KrDictQuiz.objects.exclude(pk=instance.pk).count()
        random_words_list = random.sample(range(all_words_count), _wrong_word_value)
        random_words_list.append(instance.pk)

        random_words = KrDictQuiz.objects.filter(id__in=random_words_list).values_list(
            "word", flat=True
        )
        representation["words_list"] = list(random_words)
        representation["answer_index"] = representation["words_list"].index(
            instance.word
        )

        return representation

    class Meta:
        model = KrDictQuiz
        fields = [
            "word",
            "difficulty",
        ]
