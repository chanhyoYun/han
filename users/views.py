from rest_framework.views import APIView
from users.serializers import UserSerializer, AchievementSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from users.models import User, Achievement


class UserView(APIView):
    """회원가입

    회원가입을 처리하는 뷰
    """

    def post(self, request):
        """회원가입

        post요청과 email, password를 입력 받음

        Returns:
            status 201 : "가입완료" 메세지 반환, 회원 가입
            status 400 : 입력값 에러, (serializer.errors)메세지 반환
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "가입완료"}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST
            )


class UserDetailView(APIView):
    """회원정보

    회원 정보 보기, 수정, 삭제를 처리하는 뷰
    """

    def get(self, request, user_id):
        """회원정보 조회

        Args:
            user_id : 회원 고유 아이디

        Returns:
            status 200 : 회원정보 반환
            status 404 : 회원정보 없음
        """
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)
        wear = get_object_or_404(Achievement, pk=serializer.data["wear_achievement"])
        serializer_wear = AchievementSerializer(wear)
        return Response(
            {"유저": serializer.data, "칭호": serializer_wear.data},
            status=status.HTTP_200_OK,
        )

    def patch(self, request, user_id):
        """회원정보 수정

        Args:
            request : 로그인 회원정보, 수정 데이터
            user_id : 회원 고유 pk

        Returns:
            status 200 : "수정완료" 메세지 반환, 회원정보 수정
            status 400 : (serializer.errors)메세지 반환, 입력값 오류
            status 401 : "유저가 다릅니다." 메세지 반환, 승인되지 않음
        """
        user = get_object_or_404(User, pk=user_id)
        if user == request.user:
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "수정완료"}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": f"${serializer.errors}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": "유저가 다릅니다."}, status=status.HTTP_401_UNAUTHORIZED
            )

    def delete(self, request, user_id):
        """회원 탈퇴(비활성화)

        Args:
            request : 로그인 회원정보, 수정 데이터
            user_id : 회원 고유 pk

        Returns:
            status 200 : "탈퇴완료" 메세지 반환, 회원정보 수정
            status 401 : "유저가 다릅니다." 메세지 반환, 승인되지 않음
        """
        user = get_object_or_404(User, pk=user_id)
        if user == request.user:
            user.is_active = False
            user.save()
            return Response({"message": "탈퇴완료"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "유저가 다릅니다."}, status=status.HTTP_401_UNAUTHORIZED
            )


class AchievementView(APIView):
    """칭호 관리

    전체 칭호를 보고 보유하고 있는 칭호 확인
    """

    def get(self, request, achieve_id):
        achievement = Achievement.objects.all()
        serializer = AchievementSerializer(achievement, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
