from django.db import models


class WordQuiz(models.Model):
    """크롤링 한 단어 퀴즈 모델

    퀴즈의 제목, 해설, 정답률이 저장되는 모델입니다.

    Attributes:
        title (CharField): 제목.
        explain (TextField): 해설.
        rate (PositiveIntegerField): 정답률. 양수.
    """

    title = models.CharField(max_length=100)
    explain = models.TextField()
    rate = models.PositiveIntegerField()

    def __str__(self):
        return self.title


class WordQuizOption(models.Model):
    """크롤링 한 단어 퀴즈 보기 모델

    각 퀴즈의 보기를 저장합니다.
    퀴즈id, 보기내용, 정답여부 필드가 있습니다.

    Attributes:
        quiz_id (ForeignKey): 연결된 퀴즈 인스턴스의 ID값.
        content (CharField): 보기내용.
        is_answer (BooleanField): 정답여부 Bool값. 정답 True. 오답 False.
    """

    quiz = models.ForeignKey(WordQuiz, on_delete=models.CASCADE, related_name="options")
    content = models.CharField(max_length=256)
    is_answer = models.BooleanField()

    def __str__(self):
        return f"{self.quiz.id} : {self.content}"
