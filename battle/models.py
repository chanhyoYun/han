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

    btl_title = models.CharField(max_length=255, unique=True)
    btl_created_at = models.DateTimeField(auto_now_add=True)
    btl_updated_at = models.DateTimeField(auto_now=True)
    host_user = models.OneToOneField(
        User, related_name="host_user", on_delete=models.CASCADE
    )
    max_users = models.IntegerField(default=2)
    is_public = models.BooleanField(null=False, default=False)
    room_password = models.IntegerField(null=True)


class BattleUser(models.Model):
    """배틀 참가자

    각 방 별 참가자 리스트입니다.

    Attributes:
        btl (Foreign Key) : 방 번호

        participant (Foreign Key) : 참가자
    """

    btl = models.ForeignKey(
        CurrentBattleList, related_name="battle_room_id", on_delete=models.CASCADE
    )
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    is_host = models.BooleanField(null=False, default=False)


class BattleHistory(models.Model):
    """유저 기록 모델

    유저의 배틀 정보를 기록하는 모델입니다.


    Attributes:
        btl_category (ForeignKey) : 배틀 종류

        user
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
