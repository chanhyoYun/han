from quizzes.models import Quiz
from quizzes.serializers import QuizPKserializer
import random


class QuizGenerator:
    def generate():
        quiz_objects = Quiz.objects.all()
        serializer = QuizPKserializer(quiz_objects, many=True)
        id_list = [x["pk"] for x in serializer.data]

        generate_count = 10

        quiz_ids = random.sample(id_list, k=generate_count)

        return Quiz.objects.filter(id__in=quiz_ids)
