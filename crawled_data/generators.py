from crawled_data.models import NaverQuiz, KrDictQuiz
import random


class QuizGenerator:
    def generate(model):
        quiz_objects_ids = model.objects.values_list("id", flat=True)
        id_list = list(quiz_objects_ids)

        generate_count = 10

        quiz_ids = random.sample(id_list, k=generate_count)

        return model.objects.filter(id__in=quiz_ids)
