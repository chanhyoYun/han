from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class Achievement(models.Model):
    title = models.CharField(max_length=32, verbose_name="칭호명")
    comment = models.CharField(max_length=255)

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
    player = models.ForeignKey(User, related_name="player", on_delete=models.CASCADE)
    level = models.PositiveIntegerField(default=1)
    experiment = models.PositiveIntegerField(default=0)
    max_experiment = models.IntegerField(default=100)
    day = models.PositiveIntegerField(default=0)
    quizzes_count = models.PositiveIntegerField(default=0)
