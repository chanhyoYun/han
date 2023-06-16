from django.db import models
from users.models import User


class UserQuiz(models.Model):
    """유저 제안 퀴즈 모델

    유저가 제안한 퀴즈를 담는 모델입니다.
    유저 id, 제목, 문항, 해설, 난이도, 통과 여부 필드가 있습니다.

    Attributes:
        user (ForeignKey): 문제를 제안한 user의 ID.
        title (CharField): 제목.
        content (CharField): 문항.
        explain (TextField): 해설.
        is_pass (BooleanField) : 통과 여부. True(관리자가 통과시킨 문제), False(통과되지 않은 문제)
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    content = models.CharField(max_length=256)
    explain = models.TextField()
    is_pass = models.BooleanField(default=False)


class UserQuizoption(models.Model):
    """유저 제안 퀴즈 보기 모델

    퀴즈마다의 보기를 따로 저장하는 모델입니다.
    퀴즈id, 보기내용, 정답여부 필드가 있습니다.

    Attributes:
        quiz_id (ForeignKey): 연결된 퀴즈 인스턴스의 ID값.
        content (CharField): 보기내용.
        is_answer (BooleanField): 정답여부 Bool값. 정답 True. 오답 False.
    """

    quiz = models.ForeignKey(UserQuiz, on_delete=models.CASCADE, related_name="options")
    content = models.CharField(max_length=256)
    is_answer = models.BooleanField()


class QuizReport(models.Model):
    """퀴즈 신고용 모델

    퀴즈 신고내용을 저장하는 모델입니다.

    Attributes:
        quiz_id (ForeignKey): 신고대상 퀴즈의 ID.
        user (ForeignKey): 신고한 user의 ID.
        content (BooleanField): 신고 내용.
        created_at (DateTimeField): 신고 날짜.
    """

    quiz = models.ForeignKey(UserQuiz, on_delete=models.CASCADE, related_name="reports")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
