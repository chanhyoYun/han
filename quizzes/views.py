from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.response import Response
from quizzes.serializers import (
    QuizSerializer,
    OptionSerializer,
    QuizGetSerializer,
    QuizReportSerializer,
)
from rest_framework.generics import get_object_or_404
from quizzes.models import Quiz


class QuizView(APIView):
    """퀴즈 뷰

    get요청시 퀴즈를 제공합니다.
    post요청시 퀴즈를 제안 받습니다.
    """

    def get(self, request):
        """퀴즈 뷰 get

        퀴즈를 제공합니다.

        Returns:
            정상 200: 퀴즈 데이터 제공
        """
        quiz = Quiz.objects.all()
        serializer = QuizGetSerializer(quiz, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """퀴즈 뷰 post

        퀴즈를 제안하는 요청을 받습니다.

        Returns:
            정상 201: "제출완료" 메세지
            오류 400: 올바르지 않은 입력
        """
        quiz = QuizSerializer(data=request.data["quiz"])
        if quiz.is_valid():
            save_quiz = quiz.save()
        else:
            return Response(quiz.errors, status=status.HTTP_400_BAD_REQUEST)

        options = OptionSerializer(data=request.data["options"], many=True)
        if options.is_valid():
            options.save(quiz_id=save_quiz.id)
        else:
            return Response(options.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "제출완료"}, status=status.HTTP_201_CREATED)


class QuizReportView(APIView):
    """퀴즈 신고 뷰

    post요청시 퀴즈 신고를 받습니다.
    """

    def post(self, request, quiz_id):
        """퀴즈 신고 뷰 post

        퀴즈 신고를 받습니다.

        Returns:
            정상 200: "신고완료" 메세지
            오류 400: 올바르지 않은 입력
            오류 404: 퀴즈 찾을수 없음
        """
        quiz = get_object_or_404(Quiz, id=quiz_id)
        serializer = QuizReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(quiz=quiz, user=request.user)
            return Response({"message": "신고완료"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
