import json

from channels.generic.websocket import AsyncWebsocketConsumer
from battle.models import CurrentBattleList
from channels.consumer import async_to_sync
from asgiref.sync import sync_to_async
from urllib.parse import parse_qs
from jwt import decode as jwt_decode
from channels.db import database_sync_to_async
from django.contrib.sessions.models import Session
from django.core.cache import cache
from redis import Redis
import base64


class BattleConsumer(AsyncWebsocketConsumer):
    """배틀 웹소켓 연결 클래스

    배틀 연결 및 연결 해제
    """

    @database_sync_to_async
    def get_session(self, session_key):
        return Session.objects.get(session_key=session_key)

    async def connect(self):
        """웹소켓 연결

        Args:
            self.room_name (str): 프론트엔드에서 전달받은 룸 이름
            self.room_group_name (str): 동일한 메세지를 전달받을 그룹
        """
        self.user = self.scope["user"].username
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        session_key = parse_qs(self.scope["query_string"].decode())["sessionKey"][0]
        # session = await self.get_session(session_key)
        r = Redis(host="localhost", port=6379, db=0)
        encoded_data = r.get(session_key).decode()
        # + "=" * (4 - len(r.get(session_key).decode()) % 4)
        print(base64.b64decode(encoded_data))
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # 웹소켓 연결 시점
        await self.accept()

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

    def join_game(self):
        pass
