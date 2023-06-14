from quizzes.models import Quiz
import random


class QuizGenerator:
    def generate():
        quiz_objects_ids = Quiz.objects.values_list("id", flat=True)
        id_list = list(quiz_objects_ids)

        generate_count = 10

        quiz_ids = random.sample(id_list, k=generate_count)

        return Quiz.objects.filter(id__in=quiz_ids)
