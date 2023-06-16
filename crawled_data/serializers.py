from rest_framework import serializers
from crawled_data.models import *
import random


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


class KrDictSerializer(serializers.ModelSerializer):
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
