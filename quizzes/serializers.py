from rest_framework import serializers
from quizzes.models import Quiz, Option, QuizReport


class QuizSerializer(serializers.ModelSerializer):
    """퀴즈 시리얼라이저

    퀴즈를 제안 받을때 사용됩니다.
    """

    class Meta:
        model = Quiz
        fields = "__all__"


class OptionSerializer(serializers.ModelSerializer):
    """보기 시리얼라이저

    퀴즈를 제안 받을때와
    퀴즈를 제공 할때 보기를 처리합니다.
    """

    class Meta:
        model = Option
        fields = "__all__"

    def __init__(self, instance=None, data=..., **kwargs):
        """초기화 메소드

        인스턴스 생성시 함께 생성되는 퀴즈의 id를 지정해야 하기 때문에,
        kwargs에 quiz_id를 받아옵니다.
        init을 오버라이드 해서 데이터에 실어줍니다.

        Args:
            quiz_id : 퀴즈 인스턴스의 id.
        """
        quiz_id = kwargs.pop("quiz_id", None)
        if quiz_id:
            for option in data:
                option["quiz"] = quiz_id
        super().__init__(instance, data, **kwargs)


class QuizGetSerializer(serializers.ModelSerializer):
    """퀴즈 제공 시리얼라이저

    퀴즈를 제공할때 사용됩니다.
    퀴즈마다 보기도 함께 제공합니다.
    """

    options = OptionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = "__all__"


class QuizReportSerializer(serializers.ModelSerializer):
    """퀴즈 신고 시리얼라이저

    퀴즈 신고를 받을때 사용됩니다.
    """

    class Meta:
        model = QuizReport
        fields = ("content",)
