from quizzes.models import Quiz
import random


class QuizGenerator:
    def generate():
        quiz_count = Quiz.objects.count()
        generate_count = 10

        quiz_ids = random.sample(range(1, quiz_count), k=generate_count)

        return Quiz.objects.filter(id__in=quiz_ids)
