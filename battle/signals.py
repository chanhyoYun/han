from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import CurrentBattleList
from battle.serializers import BattleListSerializer


@receiver(post_save, sender=CurrentBattleList)
def lobby_room_add(sender, instance, created, **kwargs):
    """로비에서 방 추가 웹소켓"""

    channel_layer = get_channel_layer()
    cnt_battle_list = CurrentBattleList.objects.all()
    serializer = BattleListSerializer(cnt_battle_list, many=True)
    if created:
        async_to_sync(channel_layer.group_send)(
            "lobby",
            {
                "type": "send_message",
                "method": "lobby_room_add",
                "message": serializer.data,
            },
        )
    else:
        async_to_sync(channel_layer.group_send)(
            "lobby",
            {
                "type": "send_message",
                "method": "lobby_room_updated",
                "message": serializer.data,
            },
        )


@receiver(post_delete, sender=CurrentBattleList)
def lobby_room_delete(sender, instance, **kwargs):
    """로비에서 방 삭제 웹소켓"""
    cnt_battle_list = CurrentBattleList.objects.all()
    serializer = BattleListSerializer(cnt_battle_list, many=True)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "lobby",
        {
            "type": "send_message",
            "method": "lobby_room_delete",
            "message": serializer.data,
        },
    )
