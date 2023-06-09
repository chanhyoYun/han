from django.db import models
from users.models import User


# Create your models here.
class CurrentBattleList(models.Model):
    """생성된 배틀 리스트 모델

    생성된 겨루기 리스트입니다.


    Attributes:
        btl_title (CharField) : 배틀 제목
        btl_created_at (DateTimeField) : 배틀 방 생성 시간
        btl_updated_at (DateTimeField) : 배틀 시작 시간
        host_user (ForeignKey) : 호스트 유저
        opponent_user (ForeignKey) : 상대방 유저
    """

    btl_title = models.CharField(max_length=255)
    btl_created_at = models.DateTimeField(auto_now_add=True)
    btl_updated_at = models.DateTimeField(auto_now=True)
    host_user = models.ForeignKey(
        User, related_name="host_user", on_delete=models.CASCADE
    )
    opponent_user = models.ForeignKey(
        User, related_name="opponent_user", null=True, on_delete=models.CASCADE
    )


class BattleHistory(models.Model):
    """유저 기록 모델

    유저의 배틀 정보를 기록하는 모델입니다.


    Attributes:
        btl_category (ForeignKey) : 배틀 종류
        user =
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
