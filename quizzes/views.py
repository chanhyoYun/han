from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.response import Response
from quizzes.serializers import (
    QuizSuggestSerializer,
    OptionSerializer,
    QuizSerializer,
    QuizResultSerializer,
    QuizReportSerializer,
)
from rest_framework.generics import get_object_or_404
from quizzes.models import Quiz
from quizzes.generators import QuizGenerator


class QuizView(APIView):
    """퀴즈 뷰

    get요청시 퀴즈를 제공합니다.
    post요청시 퀴즈결과를 받아 처리합니다.
    """

    def get(self, request):
        """퀴즈 뷰 get

        퀴즈를 제공합니다.

        Returns:
            정상 200: 퀴즈 데이터 제공
        """
        quiz = QuizGenerator.generate()
        serializer = QuizSerializer(quiz, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """퀴즈 뷰 post

        퀴즈풀이 결과를 받아 처리합니다.
        정답을 맞춘 문제를 세어 request유저의 경험치를 추가해줍니다.

        Returns:
            정상 200
            오류 400: 올바르지 않은 입력
            오류 401: 올바르지 않은 토큰
        """
        serializer = QuizResultSerializer(data=request.data, many=True)
        if serializer.is_valid():
            solved_quizzes = [x for x in serializer.data if x["solved"]]
            earn_exp = 10 * len(solved_quizzes)

            request.user.experiment += earn_exp
            request.user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuizSuggestView(APIView):
    """퀴즈 제안 뷰

    post요청시 퀴즈 제안을 받아 저장합니다.
    """

    def post(self, request):
        """퀴즈 뷰 post

        퀴즈를 제안하는 요청을 받아 저장합니다.

        Returns:
            정상 201: "제출완료" 메세지
            오류 400: 올바르지 않은 입력
        """
        quiz_serializer = QuizSuggestSerializer(data=request.data["quiz"])
        if quiz_serializer.is_valid():
            save_quiz = quiz_serializer.save()
        else:
            return Response(quiz_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        opt_serializer = OptionSerializer(data=request.data["options"], many=True)
        if opt_serializer.is_valid():
            opt_serializer.save(quiz_id=save_quiz.id)
        else:
            return Response(opt_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
