# chat/views.py
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from battle.models import CurrentBattleList, BattleUser
from battle.serializers import (
    BattleDetailSerializer,
    BattleCreateSerializer,
    BattleListSerializer,
)
from rest_framework import status, permissions


# def index(request):
#     return render(request, "chat/index.html")


# def room(request, room_name):
#     return render(request, "chat/room.html", {"room_name": room_name})


class GameView(APIView):
    """게임 검색 및 게임 만들기"""

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        """게임 검색

        현재 만들어진 방 탐색

        Returns:
            status 200 : 현재 존재하는 방 리스트 리턴
        """
        cnt_battle_list = CurrentBattleList.objects.all()
        serializer = BattleListSerializer(cnt_battle_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """게임 만들기

        새로운 게임 만들기

        Returns:
            status 201 : 새로운 게임 정보 리턴
            status 400 : 비로그인 시 생성 불가
        """
        serializer = BattleCreateSerializer(data=request.data)
        if serializer.is_valid():
            room_id_check = serializer.save(host_user=request.user)
            new_room = CurrentBattleList.objects.get(id=room_id_check.id)
            BattleUser.objects.create(
                btl=new_room, participant=request.user, is_host=True
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GameDetailView(APIView):
    """방에 들어갔을 때"""

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, room_id):
        """방 상세 정보

        현재 들어간 방 상세 정보

        Returns:
            roomInfo : 방 상세 정보

            participant : 방 참가자 목록
        """
        room = get_object_or_404(CurrentBattleList, id=room_id)
        serializer = BattleDetailSerializer(room)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, room_id):
        """방에 참가하기

        현재 만들어진 방 탐색

        Returns:
            status 200 : 현재 존재하는 방 리스트 리턴
        """
        room = get_object_or_404(CurrentBattleList, id=room_id)

        participant_check = BattleUser.objects.filter(participant=request.user).exists()

        if participant_check:
            return Response(
                {"message": "이미 방에 참여중입니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            new_participant = BattleUser.objects.create(
                btl=room, participant=request.user
            )
            return Response(
                {"message": "{}에 참가했습니다.".format(room.btl_title)},
                status=status.HTTP_200_OK,
            )

    def patch(self, request, room_id):
        """방 정보 수정하기

        방 제목, 최대 참가 인원 수정

        Returns:
            status 200 : 현재 존재하는 방 리스트 리턴
        """
        room = get_object_or_404(CurrentBattleList, id=room_id)
        if room.host_user != request.user:
            return Response(
                {"message": "방장만 방을 수정할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN
            )
        else:
            serializer = BattleCreateSerializer(room, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "방이 수정되었습니다."}, status.HTTP_202_ACCEPTED)

    def delete(self, request, room_id):
        """방 삭제하기

        방장만 방 삭제 가능 / 참가자 있을 때는 불가능

        Returns:
            status 204 : 방 삭제 성공
            status 403 : 방장이 아니거나, 참가자가 있거나
        """
        room = get_object_or_404(CurrentBattleList, id=room_id)

        if room.host_user != request.user:
            return Response(
                {"message": "방장만 방을 삭제할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN
            )
        elif room.battle_room_id.count() > 1:
            return Response(
                {"message": "참가자가 있을 때는 방을 삭제할 수 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            room.delete()
            return Response({"message": "방이 삭제되었습니다."}, status.HTTP_204_NO_CONTENT)
