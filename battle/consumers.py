import json

from channels.generic.websocket import AsyncWebsocketConsumer
from battle.models import CurrentBattleList, BattleUser, Notification
from users.models import User
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404

from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from users.models import User
from django.contrib.auth.models import AnonymousUser
# from battle.serializers import NotificationSerializer


class BattleConsumer(AsyncWebsocketConsumer):
    """배틀 웹소켓 연결 클래스

    배틀 연결 및 연결 해제
    """

    async def connect(self):
        """웹소켓 연결

        Args:
            self.room_name (str): 프론트엔드에서 전달받은 룸 이름
            self.room_group_name (str): 동일한 메세지를 전달받을 그룹
        """
        self.user = self.scope["user"].username
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # 웹소켓 연결 시점
        await self.accept()

        # accept되는 시점에 방에 배틀 인원에 추가
        await self.join_game()

    async def disconnect(self, close_code):
        """웹소켓 연결 해제"""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        """메세지 전송

        Args:
            text_data_json (dict): 프론트엔드 request
            message (str): 메세지 정보
        """
        text_data_json = json.loads(text_data)
        user = text_data_json["roomData"]["host"]
        message = text_data_json["message"]

        # 그룹에게 같은 메세지 전달
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message", "message": f"{user}: {message}"},
        )

    async def chat_message(self, event):
        """그룹으로부터 각자 메세지 받기

        receive 메소드에서 group_send로 메세지를 보냈을 때 받는 메소드
        """
        message = event["message"]

        # 웹소켓에 메세지 전달
        await self.send(text_data=json.dumps({"message": message}))

    @database_sync_to_async
    def join_game(self):
        user = get_object_or_404(User, username=self.user)
        battle_room = CurrentBattleList.objects.get(id=self.room_name)

        check_already_in = BattleUser.objects.filter(
            btl=battle_room, participant=user
        ).exists()

        if not check_already_in:
            BattleUser.objects.create(btl=battle_room, participant=user)
        pass


class NotificationConsumer(AsyncWebsocketConsumer):
    async def websocket_connect(self, event):
        await self.accept()
        notifications = await self.get_notification(self.scope["user"].id)
        await self.send(json.dumps(notifications))
        self.room_name = "test_consumer"
        self.room_group_name = "test_consumer_group"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

    async def websocket_receive(self, event):
        data_to_get = json.loads(event["text"])
        user_to_get = await self.get_user(int(data_to_get))
        get_of = await self.create_notification(user_to_get)
        self.room_group_name = "test_consumer_group"
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            self.room_group_name,
            {"type": "send_notification", "value": json.dumps(get_of)},
        )

    async def websocket_disconnect(self, event):
        pass

    async def send_notification(self, event):
        await self.send(json.dumps({"type": "websocket.send", "data": event}))
        
    @database_sync_to_async
    def create_notification(self, receiver, typeof="task_created", status="unread"):
        notification_to_create = Notification.objects.create(
            user_receiver=receiver, type_of_notification=typeof
        )
        return (
            notification_to_create.user_reciever.username,
            notification_to_create.type_of_notification,
        )

    @database_sync_to_async
    def get_notification(self, user_id):
        notifications = Notification.objects.filter(user_receiver=user_id)
        return list(notifications.values())
    
    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except:
            return AnonymousUser()