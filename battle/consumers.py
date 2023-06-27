import json

from channels.generic.websocket import AsyncWebsocketConsumer
from battle.models import CurrentBattleList, BattleUser, Notification
from users.models import User
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404

from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from users.models import User


class BattleConsumer(AsyncWebsocketConsumer):
    """배틀 웹소켓 연결 클래스

    배틀 연결 및 연결 해제
    """

    async def connect(self):
        """웹소켓 연결"""
        await self.accept()
        notifications = await self.get_notification()
        await self.send(json.dumps(notifications))

    async def disconnect(self, code):
        """웹소켓 연결해제"""
        # await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        type_dict = {
            "join_room": self.receive_join_room,
            "invitation": self.receive_invitation,
            "chat_message": self.receive_chat_message,
        }
        await type_dict[data["type"]](data)

    async def receive_join_room(self, data):
        self.room_name = data["room"]
        self.room_group_name = "chat_%s" % self.room_name
        await self.join_room()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

    async def receive_invitation(self, data):
        receiver = data["receiver"]
        notification = await self.create_notification(receiver)
        chat_message = {"type": "send_message", "message": notification}
        await self.channel_layer.group_send(f"user_{receiver}", chat_message)

    async def receive_chat_message(self, data):
        user = self.scope["user"]
        message = data["message"]
        chat_message = {"type": "send_message", "message": f"{user}: {message}"}
        await self.channel_layer.group_send(self.room_group_name, chat_message)

    async def send_message(self, event):
        """그룹으로부터 각자 메세지 받기

        receive 메소드에서 group_send로 메세지를 보냈을 때 받는 메소드
        """
        message = event["message"]

        # 웹소켓에 메세지 전달
        await self.send(text_data=json.dumps({"message": message}))

    @database_sync_to_async
    def join_room(self):
        user = self.scope["user"]
        battle_room = CurrentBattleList.objects.get(id=self.room_name)

        check_already_in = BattleUser.objects.filter(
            btl=battle_room, participant=user
        ).exists()

        if not check_already_in:
            BattleUser.objects.create(btl=battle_room, participant=user)

    @database_sync_to_async
    def get_notification(self):
        user = self.scope["user"]
        notifications = Notification.objects.filter(user_receiver=user.id)
        return list(notifications.values())

    @database_sync_to_async
    def create_notification(self, receiver, typeof="invitation"):
        user = User.objects.get(id=receiver)
        notification = Notification.objects.create(
            user_sender=self.scope["user"],
            user_receiver=user,
            type_of_notification=typeof,
        )
        return (
            notification.user_sender.username,
            notification.type_of_notification,
        )
