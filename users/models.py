from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class Achievement(models.Model):
    """유저 칭호 모델

    Attributes:
        title (CharField) : 칭호명
        comment (CharField) : 칭호 설명
        image_url (CharField) : 칭호 이미지 주소
    """

    title = models.CharField(max_length=32, verbose_name="칭호명")
    comment = models.CharField(max_length=255)
    image_url = models.CharField(max_length=255, verbose_name="이미지 주소")

    def __str__(self):
        return self.title


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """유저 모델

    Attributes:
        email (EmailField) : 로그인 이메일
        username (CharField) : 닉네임
        is_active (BooleanField) : 활성화 여부
        is_admin (BooleanField) : 관리자 계정 여부
        image (ImageField) : 프로필사진 필드
        achieve (ManyToManyField) : 보유 칭호 필드
        wear_achievement (IntegerField) : 착용중인 칭호 정보
        followings (ManyToManyField) : 유저 팔로잉
    """

    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )

    username = models.CharField(max_length=255, blank=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    image = models.ImageField(blank=True)

    achieve = models.ManyToManyField("Achievement", blank=True, verbose_name="achieves")
    wear_achievement = models.IntegerField(default=-1)

    followings = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers", blank=True
    )

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class UserInfo(models.Model):
    """유저 정보 모델

    Attributes:
        player (ForeignKey) : 연결되어 있는 유저
        level (PositiveIntegerField) : 유저 레벨
        experiment (PositiveIntegerField) : 유저 경험치
        max_experiment (IntegerField) : 레벨에 비례한 경험치통
        total_study_day (PositiveIntegerField): 총 학습일수
        day (PositiveIntegerField) : 연속 출석일수
        attend (DateTimeField) : 마지막 학습 날짜
        quizzes_count (PositiveIntegerField) : 푼 문제 갯수
        battlepoint (PositiveIntegerField) : 함께 겨루기에서 맞춘 문제 개수
    """

    player = models.ForeignKey(User, related_name="player", on_delete=models.CASCADE)
    level = models.PositiveIntegerField(default=1)
    experiment = models.PositiveIntegerField(default=0)
    max_experiment = models.IntegerField(default=100)
    total_study_day = models.PositiveIntegerField(default=0)
    day = models.PositiveIntegerField(default=0)
    attend = models.DateTimeField(
        auto_now=False, auto_now_add=True, blank=True, null=True
    )
    quizzes_count = models.PositiveIntegerField(default=0)
    battlepoint = models.PositiveIntegerField(default=0)


class UserTimestamp(models.Model):
    """유저 게임 플레이 기록 모델

    유저가 혼자 문제 풀기를 시도하고 끝낸 시간을 기록하는 모델

    Attributes:
        user (ForeignKey) : 유저
        quiz_start (DateTimeField) : 퀴즈 시작시각
        quiz_end (DateTimeField) : 퀴즈 제출시각
    """

    user = models.ForeignKey(User, related_name="timestamp", on_delete=models.CASCADE)
    quiz_start = models.DateTimeField(auto_now_add=True)
    quiz_end = models.DateTimeField(null=True)
