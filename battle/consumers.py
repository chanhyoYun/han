import json

from channels.generic.websocket import AsyncWebsocketConsumer
from battle.models import CurrentBattleList, BattleUser, Notification
from users.models import User
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404

from crawled_data.generators import QuizGenerator
from .serializers import BattleParticipantSerializer


class BattleConsumer(AsyncWebsocketConsumer):
    """배틀 웹소켓 연결 클래스

    배틀 연결 및 연결 해제
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quizzes = []
        self.quiz_participant = 0
        self.quiz_count = 0

    async def connect(self):
        """웹소켓 연결"""
        await self.accept()
        self.room_group_name = "user_%s" % self.scope["user"].id
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        notifications = await self.get_notification()
        message = {
            "type": "send_message",
            "method": "notification",
            "message": notifications,
        }
        await self.channel_layer.group_send(self.room_group_name, message)

    async def disconnect(self, code):
        """웹소켓 연결해제"""
        # await self.leave_room()

    async def receive(self, text_data):
        """웹소켓 receive

        프론트에서 받아온 데이터를 처리
        Args:
            text_data : 프론트에서 넘어오는 데이터.
                        {"type" : "유형", **kwargs}
        """
        data = json.loads(text_data)
        type_dict = {
            "join_room": self.receive_join_room,
            "invitation": self.receive_invitation,
            "read_notification": self.receive_read_notification,
            "chat_message": self.receive_chat_message,
            "start_game": self.receive_start_game,
            "correct_answer": self.receive_correct_answer,
            "result": self.receive_result,
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
        chat_message = {
            "type": "send_message",
            "method": "notification",
            "message": notification,
        }
        await self.channel_layer.group_send(f"user_{receiver}", chat_message)

    async def receive_read_notification(self, data):
        notification_id = data["notification"]
        await self.read_notification(notification_id)

    async def receive_chat_message(self, data):
        user = self.scope["user"]
        message = data["message"]
        chat_message = {
            "type": "send_message",
            "method": "chat_message",
            "message": f"{user}: {message}",
        }
        await self.channel_layer.group_send(self.room_group_name, chat_message)

    async def receive_start_game(self, data):
        """게임 진행

        퀴즈를 진행하는 메소드.
        참가자가 2명 이상일 때는 게임을 진행, 그 이외에는 에러 메세지를 전송
        Args:
            data : 프론트에서 받아온 데이터.
                    {"type":"유형", "message":"메세지"}
        """
        self.quiz_participant = await self.get_quiz_participant()

        if self.quiz_participant > 1:
            self.quiz_count = 0
            await self.get_quiz()
            message = data["message"]
            start_message = {
                "type": "send_message",
                "method": "chat_message",
                "message": f"알림: {message}",
            }
            quiz_message = {
                "type": "send_message",
                "method": "send_quiz",
                "quiz": self.quizzes,
            }
            await self.channel_layer.group_send(self.room_group_name, start_message)
            await self.channel_layer.group_send(self.room_group_name, quiz_message)
        else:
            error_message = {
                "type": "send_message",
                "method": "chat_message",
                "message": "알림: 유저가 2명 이상이어야 게임이 시작 가능합니다.",
            }
            await self.channel_layer.group_send(self.room_group_name, error_message)

    async def receive_correct_answer(self, data):
        """정답 처리

        프론트에서 온 메세지에 맞춰 정답 처리를 하는 메소드.
        quiz_count가 9개 이상이 되면(10문제가 출제되면) 결과 처리 메소드로 전송
        Args:
            data : 프론트에서 받아온 데이터.
                    {"type":"유형", "message":"메세지", "end":true}
        """
        end = data.get("end")
        if not end:
            user = self.scope["user"]
            message = data["message"]
            next_message = {
                "type": "send_message",
                "method": "chat_message",
                "message": f"알림: {user} {message}",
            }
            await self.channel_layer.group_send(self.room_group_name, next_message)
            self.quiz_count += 1

            next_message = {
                "type": "send_message",
                "method": "next_quiz",
                "message": "다음 문제로 넘어갑니다.",
            }
            await self.channel_layer.group_send(self.room_group_name, next_message)
        else:
            end_message = {
                "type": "send_message",
                "method": "end_quiz",
                "message": "게임이 종료되었습니다. 정보를 집계합니다.",
            }
            await self.channel_layer.group_send(self.room_group_name, end_message)

    async def receive_result(self, event):
        user = self.scope["user"]
        result_message = {
            "type": "send_message",
            "method": "chat_message",
            "message": f"{user}의 정답 개수 : {self.quiz_count}",
        }
        await self.channel_layer.group_send(self.room_group_name, result_message)

    async def send_message(self, event):
        """그룹으로부터 각자 메세지 받기

        receive 메소드에서 group_send로 메세지를 보냈을 때 받는 메소드
        """

        # 웹소켓에 메세지 전달
        await self.send(text_data=json.dumps(event))

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
    def leave_room(self):
        """방 나가기

        disconnect 시 유저가 방을 나가게 하는 메소드
        is_host = True인 경우 방 자체를 삭제
        """
        user = self.scope["user"]
        room_user = BattleUser.objects.get(participant=user)
        if room_user.is_host:
            battle_room = CurrentBattleList.objects.get(id=self.room_name)
            battle_room.delete()
        else:
            room_user.delete()

    @database_sync_to_async
    def get_quiz(self):
        """퀴즈 생성

        게임 시작 시 퀴즈 10개를 일괄 생성하는 메소드
        """
        quizzes = QuizGenerator([0, 0, 10, 0])
        self.quizzes = quizzes.generator()["fill_in_the_blank"]

    @database_sync_to_async
    def get_quiz_participant(self):
        """퀴즈 참가자 수 확인

        함수 호출 시의 퀴즈 참가자 수를 확인 후 return하는 메소드
        """
        battle_room = CurrentBattleList.objects.get(id=self.room_name)
        quiz_participant = BattleUser.objects.filter(btl=battle_room)
        serializers = BattleParticipantSerializer(instance=quiz_participant, many=True)
        return len(serializers.data)

    @database_sync_to_async
    def get_notification(self):
        notifications = Notification.objects.filter(
            user_receiver=self.scope["user"],
            status="unread",
        )
        return [
            {"id": row.id, "sender": row.user_sender.username, "room": row.btl.id}
            for row in notifications
        ]

    @database_sync_to_async
    def create_notification(self, receiver, typeof="invitation"):
        user = User.objects.get(id=receiver)
        notification = Notification.objects.create(
            user_sender=self.scope["user"],
            user_receiver=user,
            btl_id=self.room_name,
            type_of_notification=typeof,
        )
        return {
            "id": notification.id,
            "sender": notification.user_sender.username,
            "room": notification.btl.id,
        }

    @database_sync_to_async
    def read_notification(self, notification_id):
        notification = Notification.objects.get(id=notification_id)
        notification.status = "read"
        notification.save()
