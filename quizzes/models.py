from django.db import models


class Quiz(models.Model):
    """퀴즈 모델

    퀴즈의 제목, 문항, 설명, 난이도가 저장되는 모델입니다.

    Attributes:
        title (CharField): 제목.
        content (CharField): 문항.
        explain (TextField): 설명.
        difficulty (PositiveIntegerField): 난이도. 양수.
    """

    title = models.CharField(max_length=30)
    content = models.CharField(max_length=256)
    explain = models.TextField()
    difficulty = models.PositiveIntegerField()


class Option(models.Model):
    """보기 모델

    퀴즈마다의 보기를 따로 저장하는 모델입니다.
    퀴즈id, 보기내용, 정답여부 필드가 있습니다.

    Attributes:
        quiz_id (ForeignKey): 연결된 퀴즈 인스턴스의 ID값.
        content (CharField): 보기내용.
        is_answer (BooleanField): 정답여부 Bool값. 정답 True. 오답 False.
    """

    quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    content = models.CharField(max_length=256)
    is_answer = models.BooleanField()
