from rest_framework.views import APIView
from users.serializers import UserSerializer, AchievementSerializer, RankingSerializer
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import get_object_or_404, ListAPIView
from users.models import User, Achievement
from rest_framework_simplejwt.views import TokenObtainPairView
from users.serializers import CustomTokenObtainPairSerializer
import os
from django.http import JsonResponse
import jwt


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
        print(request)
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
        # return Response(serializer.data, status=status.HTTP_200_OK)
        if serializer.data["wear_achievement"] != -1:
            wear = get_object_or_404(
                Achievement, pk=serializer.data["wear_achievement"]
            )
            serializer_wear = AchievementSerializer(wear)
            return Response(
                {"유저": serializer.data, "칭호": serializer_wear.data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"유저": serializer.data, "칭호": "null"},
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


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            print(serializer.data)
            # print(user_email)

            # JWT 토큰 생성 및 쿠키 설정
            access_token = jwt.encode(
                {"user_email": user_email},
                os.environ.get("SECRET_KEY"),
                algorithm=os.environ.get("ALGORITHM"),
            ).decode("utf-8")
            response.set_cookie("access_token", access_token)

            return response
        else:
            return Response(
                {"message": "회원정보가 맞지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )


class RankingView(ListAPIView):
    """랭킹 조회

    랭킹보드용 유저 순위를 제공하는 뷰
    """

    serializer_class = RankingSerializer
    queryset = User.objects.all().order_by("-experiment")

    def get_queryset(self):
        """랭킹 조회

        get요청에 대해 쿼리셋을 생성하여 반환합니다.
        시리얼라이저와 페이지네이션이 동작합니다.
        기본 쿼리셋은 경험치순

        Args:
            type(query_param) : 쿼리 파라미터 type 유무 확인

        Returns:
            status 200 : 전체 유저 랭킹순
        """
        queryset_select = {"battle": self.queryset_battle}
        query_param_check = self.request.GET.get("type", None)
        return queryset_select.get(query_param_check, super().get_queryset)()

    def queryset_battle(self):
        """배틀랭킹 조회

        type=battle시, 쿼리셋을 배틀랭킹으로 생성합니다.
        """
        return User.objects.all().order_by("-battlepoint")
