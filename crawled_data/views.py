from rest_framework.decorators import APIView
from rest_framework.response import Response
from crawled_data.generators import QuizGenerator


class PuzzleCreateView(APIView):
    def get(self, request):
        quiz_generator = QuizGenerator([3, 3, 3, 1])
        quiz = quiz_generator.generator()
        return Response(quiz)
