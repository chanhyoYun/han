from rest_framework import status, permissions
from rest_framework.decorators import APIView
from rest_framework.response import Response
from quizzes.serializers import (
    QuizSuggestSerializer,
    OptionSerializer,
    QuizResultSerializer,
    QuizReportSerializer,
)
from users.user_info import check_user_info


class QuizResultView(APIView):
    """퀴즈 뷰

    post요청시 퀴즈결과를 받아 처리합니다.
    """

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
            check_user_info(serializer.data, request.user.id)

            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuizSuggestView(APIView):
    """유저 퀴즈 제안 뷰

    post요청시 퀴즈 제안을 받아 저장합니다.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """유저 퀴즈 뷰 post

        퀴즈를 제안하는 요청을 받아 저장합니다.

        Returns:
            정상 201: "제출완료" 메세지
            오류 400: 올바르지 않은 입력
        """
        user = request.user
        quiz_data = request.data["quiz"]
        quiz_data["user"] = user.id
        quiz_serializer = QuizSuggestSerializer(data=quiz_data)
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

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """퀴즈 신고 뷰 post

        퀴즈 신고를 받습니다.

        Returns:
            정상 200: "신고완료" 메세지
            오류 400: 올바르지 않은 입력
            오류 404: 퀴즈 찾을수 없음
        """
        user = request.user
        report_data = request.data
        report_data["user"] = user.id
        serializer = QuizReportSerializer(data=report_data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "신고가 완료되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
