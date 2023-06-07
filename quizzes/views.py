from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.response import Response
from quizzes.serializers import QuizSerializer, OptionSerializer


class QuizView(APIView):
    """퀴즈 뷰

    post요청시 퀴즈를 제안 받습니다.
    """

    def post(self, request):
        """퀴즈 뷰 post

        퀴즈를 제안하는 요청을 받습니다.
        """
        quiz = QuizSerializer(data=request.data["quiz"])
        if quiz.is_valid():
            save_quiz = quiz.save()
        else:
            return Response(quiz.errors, status=status.HTTP_400_BAD_REQUEST)

        options = OptionSerializer(
            data=request.data["options"], many=True, quiz_id=save_quiz.id
        )
        if options.is_valid():
            options.save()
        else:
            return Response(options.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "제출완료"}, status=status.HTTP_201_CREATED)
