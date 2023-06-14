from django.db import models


class NaverQuiz(models.Model):
    """네이버 퀴즈에서 크롤링 한 퀴즈 모델

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


class NaverQuizOption(models.Model):
    """네이버 퀴즈에서 크롤링 한 퀴즈 보기 모델

    각 퀴즈의 보기를 저장합니다.
    퀴즈id, 보기내용, 정답여부 필드가 있습니다.

    Attributes:
        quiz_id (ForeignKey): 연결된 퀴즈 인스턴스의 ID값.
        content (CharField): 보기내용.
        is_answer (BooleanField): 정답여부 Bool값. 정답 True. 오답 False.
    """

    quiz = models.ForeignKey(
        NaverQuiz, on_delete=models.CASCADE, related_name="options"
    )
    content = models.CharField(max_length=256)
    is_answer = models.BooleanField()

    def __str__(self):
        return f"{self.quiz.id} : {self.content}"


class KrDictQuiz(models.Model):
    """한국어 기초 사전 단어 저장 모델

    한국어 기초 사전에 등재 된 단어들을 담는 모델입니다.

    Attributes:
        word (CharField): 단어.
        difficulty (PositiveIntegerField): 한국어 기초 사전이 지정한 단어 난이도. 0(미분류), 1(초급), 2(중급), 3(고급)
    """

    word = models.CharField(max_length=128)
    difficulty = models.PositiveIntegerField()


class KrDictQuizExplain(models.Model):
    """한국어 기초 사전 단어 설명 저장 모델

    한국어 기초 사전에 등재 된 단어들의 설명을 담는 모델입니다.

    Attributes:
        dict_word_id (ForeignKey): 연결된 사전 단어 인스턴스의 ID값
        content (CharField): 설명 내용.
    """

    dict_word = models.ForeignKey(
        KrDictQuiz, on_delete=models.CASCADE, related_name="explains"
    )
    content = models.CharField(max_length=256)


class KrDictQuizExample(models.Model):
    """한국어 기초 사전 단어 예시 저장 모델

    한국어 기초 사전에 등재 된 단어들의 예시를 담는 모델입니다.

    Attributes:
        dict_word_id (ForeignKey): 연결된 사전 단어 인스턴스의 ID값
        word_type (PositiveIntegerField) : 예시 타입. 0(구), 1(문장).
        content (CharField): 예시 내용.
    """

    dict_word = models.ForeignKey(
        KrDictQuiz, on_delete=models.CASCADE, related_name="examples"
    )
    word_type = models.PositiveIntegerField()
    content = models.CharField(max_length=256)
