from rest_framework.decorators import APIView
from rest_framework.response import Response
from crawled_data.generators import QuizGenerator


class PuzzleCreateView(APIView):
    """퍼즐 생성 View"""

    def get(self, request):
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
        return Response(quiz)
