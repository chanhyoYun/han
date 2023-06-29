from django.db import models
from users.models import User


class CurrentBattleList(models.Model):
    """생성된 배틀 리스트 모델

    생성된 겨루기 리스트입니다.


    Attributes:
        btl_title (CharField) : 배틀 제목

        btl_created_at (DateTimeField) : 배틀 방 생성 시간

        btl_updated_at (DateTimeField) : 배틀 시작 시간

        host_user (ForeignKey) : 호스트 유저

        max_users (IntegerField) : 최대 인원

        is_private (BooleanField) : 비공개방 여부

        room_password (IntegerField) : 비공개방 비밀번호

        btl_start (BooleanField) : 게임 시작 여부
    """

    btl_category_choices = (
        ("A", "종합"),
        ("C", "십자말풀이"),
        ("D", "단어맞추기"),
    )

    btl_title = models.CharField(max_length=60, unique=True)
    btl_category = models.CharField(max_length=5, choices=btl_category_choices)
    btl_created_at = models.DateTimeField(auto_now_add=True)
    btl_updated_at = models.DateTimeField(auto_now=True)
    host_user = models.OneToOneField(
        User, related_name="host_user", on_delete=models.CASCADE
    )
    max_users = models.IntegerField(default=2)
    is_private = models.BooleanField(null=False, default=False)
    room_password = models.IntegerField(null=True)
    btl_start = models.BooleanField(default=False)


class BattleUser(models.Model):
    """배틀 참가자

    각 방 별 참가자 리스트입니다.

    Attributes:
        btl (Foreign Key) : 방 번호

        participant (Foreign Key) : 참가자

        is_host (BooleanField) : 참가자 방장 여부
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


class Notification(models.Model):
    """알림 모델

    알림 모델입니다.
    """

    user_sender = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="user_sender",
        on_delete=models.CASCADE,
    )
    user_receiver = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="user_reciever",
        on_delete=models.CASCADE,
    )
    btl = models.ForeignKey(CurrentBattleList, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=264, null=True, blank=True, default="unread")
    type_of_notification = models.CharField(max_length=264, null=True, blank=True)
