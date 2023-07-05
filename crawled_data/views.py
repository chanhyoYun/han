from rest_framework.decorators import APIView
from rest_framework.response import Response
from crawled_data.generators import QuizGenerator
from users.models import UserTimestamp
from django.contrib.auth.models import AnonymousUser


class PuzzleCreateView(APIView):
    """퍼즐 생성 View"""

    def get(self, request):
        """퀴즈 생성 뷰

        QuizGenerator로 퀴즈를 생성해서 Return

        Returns:
            quiz: 유형별로 생성한 퀴즈 데이터
        """
        param = request.GET.get("type")
        param_dict = {
            "1": [10, 0, 0, 0],
            "2": [0, 10, 0, 0],
            "3": [0, 0, 10, 0],
            "4": [0, 0, 0, 1],
        }
        if param:
            quiz_generator = QuizGenerator(param_dict[param])
        else:
            quiz_generator = QuizGenerator([3, 3, 4, 0])
        quiz = quiz_generator.generator()
        if not isinstance(request.user, AnonymousUser):
            # user = User.objects.get(pk=request.user.id)
            UserTimestamp.objects.create(user=request.user)
        return Response(quiz)
