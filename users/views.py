from rest_framework.views import APIView
from users.serializers import (
    UserSerializer,
    AchievementSerializer,
    RankingSerializer,
    PasswordResetSerializer,
    UserInfoSerializer,
    CustomTokenObtainPairSerializer,
    UserViewSerializer,
)
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import get_object_or_404, ListAPIView
from users.models import User, Achievement, UserInfo
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from users.customtoken import user_email_verify_token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserView(APIView):
    """회원가입

    회원가입을 처리하는 뷰
    """

    def post(self, request):
        """회원가입

        Args:
            request : email, password, username 입력 받음

        Returns:
            status 201 : "가입완료" 메세지 반환, 회원 가입
            status 400 : 입력값 에러, (serializer.errors)메세지 반환
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "유저 인증 이메일을 전송했습니다."}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST
            )


class EmailVerifyView(APIView):
    """일반 유저 이메일 인증

    일반 유저 가입 시 사용 가능한 이메일인지 확인해주는 뷰
    """

    def get(self, request, uidb64, token):
        """일반 유저 이메일 인증

        Args:
            request : 클라이언트 요청
            uidb64 : 인코딩 한 유저 아이디
            token : 해당 유저의 토큰

        Returns:
            status 200 : 인증 완료 메세지 반환. 유저의 is_active가 True로 변환
            status 400 : keyError 발생 메세지 반환.
            status 401 : 인증 실패 메세지 반환. check_token 메소드를 통과하지 못함
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if user_email_verify_token.check_token(user, token):
                User.objects.filter(pk=uid).update(is_active=True)
                return Response(
                    {"message": "이메일 인증이 완료되었습니다."}, status=status.HTTP_200_OK
                )
            return Response(
                {"error": "이메일 인증에 실패했습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
        except KeyError:
            return Response(
                {"error": "KEY ERROR가 발생했습니다."}, status=status.HTTP_400_BAD_REQUEST
            )


class PasswordResetView(APIView):
    """비밀번호 초기화

    일반 유저의 비밀번호를 초기화 시켜주는 뷰
    """

    def put(self, request):
        """비밀번호 초기화

        Args:
            request : 비밀번호를 초기화 할 계정의 이메일

        Returns:
            status 200 : 임시 비밀번호로 초기화 완료
            status 400 : 비밀번호 초기화에 실패
        """
        user = get_object_or_404(User, email=request.data.get("email"))
        serializer = PasswordResetSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "비밀번호 초기화 이메일을 전송했습니다."}, status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    """회원정보

    회원 정보 보기, 수정, 삭제를 처리하는 뷰
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, user_id):
        """회원정보 조회

        Args:
            user_id : 회원 고유 아이디

        Returns:
            status 200 : 회원정보 반환
            status 404 : 회원정보 없음
        """
        user = get_object_or_404(User, id=user_id)
        serializer = UserViewSerializer(user)
        user_info = get_object_or_404(UserInfo, player_id=user_id)
        serializer_info = UserInfoSerializer(user_info)
        if serializer.data["wear_achievement"] != -1:
            wear = get_object_or_404(
                Achievement, pk=serializer.data["wear_achievement"]
            )
            serializer_wear = AchievementSerializer(wear)
            return Response(
                {
                    "유저": serializer.data,
                    "정보": serializer_info.data,
                    "칭호": serializer_wear.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"유저": serializer.data, "정보": serializer_info.data, "칭호": "null"},
                status=status.HTTP_200_OK,
            )

    def patch(self, request, user_id):
        """회원정보 수정

        Args:
            request : username, wear_achievement, image 수정 데이터 입력 받음
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
        """모든 칭호 보기

        Returns:
            status 200 : 모든 achieve 데이터
        """
        achievement = Achievement.objects.all()
        serializer = AchievementSerializer(achievement, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowView(APIView):
    """팔로우

    유저끼리의 팔로우
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        """팔로우 완료, 취소

        Args:
            request : 로그인 한 유저 정보
            user_id : 유저 고유 id값

        Returns:
            status 200 : 내 팔로잉 목록에 해당 유저 추가
            status 204 : 내 팔로잉 목록에서 해당 유저 제거
            status 400 : 자기 자신은 팔로우 할 수 없음
            stauts 404 : 유저를 찾을 수 없음
        """
        you = get_object_or_404(User, id=user_id)
        me = request.user
        if me != you:
            if me in you.followers.all():
                you.followers.remove(me)
                return Response("팔로우 취소", status=status.HTTP_204_NO_CONTENT)
            else:
                you.followers.add(me)
                return Response("팔로우 완료", status=status.HTTP_200_OK)
        else:
            return Response("자기 자신은 팔로우 불가합니다.", status=status.HTTP_400_BAD_REQUEST)


class RankingView(ListAPIView):
    """랭킹 조회

    랭킹보드용 유저 순위를 제공하는 뷰
    """

    serializer_class = RankingSerializer
    queryset = UserInfo.objects.filter(player__is_active=True).order_by(
        "-level", "-experiment"
    )

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
