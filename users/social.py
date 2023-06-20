from django.shortcuts import redirect, render
import os
from json import JSONDecodeError
from django.http import JsonResponse
import requests
from rest_framework import status
from allauth.socialaccount.models import SocialAccount
from users.models import User
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.naver import views as naver_view
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view
from users.customtoken import CustomAccessToken, CustomRefreshToken
from users.models import UserInfo

state = os.environ.get("STATE")
BASE_URL = "http://127.0.0.1:5500/"
CALLBACK_URI = BASE_URL + "html/home.html"


# 구글 로그인
def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    return redirect(
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={CALLBACK_URI}&scope={scope}"
    )


def google_callback(request):
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.GET.get("code")

    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={CALLBACK_URI}&state={state}"
    )

    token_req_json = token_req.json()
    error = token_req_json.get("error")

    if error is not None:
        raise JSONDecodeError(error)

    access_token = token_req_json.get("access_token")
    email_req = requests.get(
        f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
    )
    email_req_status = email_req.status_code

    if email_req_status != 200:
        return Response(
            {"message": "이메일을 받아오지 못했습니다."}, status=status.HTTP_400_BAD_REQUEST
        )

    email_req_json = email_req.json()
    email = email_req_json.get("email")

    try:
        user = User.objects.get(email=email)

        social_user = SocialAccount.objects.get(user=user)

        if social_user.provider != "google":
            return JsonResponse(
                {"message": "소셜이 일치하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = {
            "access_token": access_token,
            "code": code,
            "email": email,
            "log": False,
        }
        return JsonResponse(data, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        data = {
            "access_token": access_token,
            "code": code,
            "email": email,
            "log": True,
        }
        return JsonResponse(data, status=status.HTTP_200_OK)

    except SocialAccount.DoesNotExist:
        return JsonResponse(
            {"message": "소셜로그인 유저가 아닙니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = CALLBACK_URI
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        accept = super().post(request, *args, **kwargs)
        accept_status = accept.status_code

        if accept_status != 200:
            return Response({"message": "구글 소셜 로그인 실패"}, status=accept_status)

        user = User.objects.get(email=request.data["email"])

        if request.data["log"]:
            UserInfo.objects.create(player=user)

        access_token = CustomAccessToken.for_user(user)
        refresh_token = CustomRefreshToken.for_user(user)

        return Response(
            {"refresh": str(refresh_token), "access": str(access_token)},
            status=status.HTTP_200_OK,
        )


def kakao_login(request):
    rest_api_key = os.environ.get("SOCIAL_AUTH_KAKAO_CLIENT_ID")
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={rest_api_key}&redirect_uri={CALLBACK_URI}"
    )


@api_view(["GET", "POST"])
def kakao_callback(request):
    rest_api_key = os.environ.get("SOCIAL_AUTH_KAKAO_CLIENT_ID")
    code = request.GET.get("code")

    token_request = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={CALLBACK_URI}&code={code}"
    )

    token_request_json = token_request.json()

    error = token_request_json.get("error")

    if error is not None:
        access_token = token_request_json.get("access_token")
        requests.post(
            "https://kapi.kakao.com/v1/user/unlink",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        raise JSONDecodeError(error)

    access_token = token_request_json.get("access_token")

    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()
    kakao_account = profile_json.get("kakao_account")
    """
    kakao_account에서 이메일 외에
    카카오톡 프로필 이미지, 배경 이미지 url 가져올 수 있음
    print(kakao_account) 참고
    """
    email = kakao_account.get("email")

    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return Response(
                {"message": "소셜 로그인이 아닙니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if social_user.provider != "kakao":
            return Response(
                {"message": "카카오 소셜이 아닙니다. 계정을 확인해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = {
            "access_token": access_token,
            "code": code,
            "email": email,
            "log": False,
        }
        return Response(data, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        data = {
            "access_token": access_token,
            "code": code,
            "email": email,
            "log": True,
        }
        return Response(data, status=status.HTTP_200_OK)


class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = CALLBACK_URI

    def post(self, request, *args, **kwargs):
        accept = super().post(request, *args, **kwargs)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({"message": "카카오 소셜 로그인 실패"}, status=accept_status)

        user = User.objects.get(email=request.data["email"])

        if request.data["log"]:
            UserInfo.objects.create(player=user)

        access_token = CustomAccessToken.for_user(user)
        refresh_token = CustomRefreshToken.for_user(user)

        return Response(
            {"refresh": str(refresh_token), "access": str(access_token)},
            status=status.HTTP_200_OK,
        )


def naver_login(request):
    client_id = os.environ.get("SOCIAL_AUTH_NAVER_CLIENT_ID")
    return redirect(
        f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={client_id}&state=STATE_STRING&redirect_uri={CALLBACK_URI}"
    )


@api_view(["GET", "POST"])
def naver_callback(request):
    client_id = os.environ.get("SOCIAL_AUTH_NAVER_CLIENT_ID")
    client_secret = os.environ.get("SOCIAL_AUTH_NAVER_SECRET")
    code = request.GET.get("code")
    state_string = request.GET.get("state")

    # code로 access token 요청
    token_request = requests.get(
        f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&code={code}&state={state_string}"
    )
    token_response_json = token_request.json()

    error = token_response_json.get("error", None)
    if error is not None:
        raise JSONDecodeError(error)

    access_token = token_response_json.get("access_token")

    profile_request = requests.post(
        "https://openapi.naver.com/v1/nid/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()

    email = profile_json.get("response").get("email")

    if email is None:
        return Response(
            {"message": "이메일을 가져오지 못했습니다."}, status=status.HTTP_400_BAD_REQUEST
        )

    # 받아온 네이버 계정으로 회원가입/로그인 시도
    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return Response(
                {"message": "소셜로그인이 아닙니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if social_user.provider != "naver":
            return Response(
                {"message": "네이버 소셜이 아닙니다. 계정을 확인해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 기존에 Google로 가입된 유저
        data = {
            "access_token": access_token,
            "code": code,
            "email": email,
            "log": False,
        }
        return Response(data, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        data = {"access_token": access_token, "code": code, "email": email, "log": True}
        return Response(data, status=status.HTTP_200_OK)


class NaverLogin(SocialLoginView):
    adapter_class = naver_view.NaverOAuth2Adapter
    callback_url = CALLBACK_URI
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        accept = super().post(request, *args, **kwargs)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({"message": "네이버 소셜 로그인 실패"}, status=accept_status)

        user = User.objects.get(email=request.data["email"])

        if request.data["log"]:
            UserInfo.objects.create(player=user)

        access_token = CustomAccessToken.for_user(user)
        refresh_token = CustomRefreshToken.for_user(user)

        return Response(
            {"refresh": str(refresh_token), "access": str(access_token)},
            status=status.HTTP_200_OK,
        )
