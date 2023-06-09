from django.shortcuts import redirect
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
from dj_rest_auth.registration.serializers import SocialLoginSerializer

state = os.environ.get("STATE")
BASE_URL = "http://127.0.0.1:8000/"
GOOGLE_CALLBACK_URI = BASE_URL + "users/google/callback/"


# 구글 로그인
def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    return redirect(
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}"
    )


def google_callback(request):
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.GET.get("code")

    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}"
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
        return JsonResponse(
            {"err_msg": "failed to get email"}, status=status.HTTP_400_BAD_REQUEST
        )

    email_req_json = email_req.json()
    email = email_req_json.get("email")

    try:
        user = User.objects.get(email=email)

        social_user = SocialAccount.objects.get(user=user)

        if social_user.provider != "google":
            return JsonResponse(
                {"err_msg": "no matching social type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}users/google/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signin"}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop("user", None)
        print(accept_json)
        # return JsonResponse(accept_json)
        return redirect("http://127.0.0.1:5500/html/index.html")
    # {"key": dfssdfsdfsd} 로 받아옴.. 왜?

    except User.DoesNotExist:
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}users/google/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signup"}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop("user", None)
        print(accept_json)
        # return JsonResponse(accept_json)
        return redirect("http://127.0.0.1:5500/html/index.html")

    except SocialAccount.DoesNotExist:
        return JsonResponse(
            {"err_msg": "email exists but not social user"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client
    serializer_class = SocialLoginSerializer


KAKAO_CALLBACK_URI = BASE_URL + "users/kakao/callback/"


def kakao_login(request):
    rest_api_key = os.environ.get("SOCIAL_AUTH_KAKAO_CLIENT_ID")
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code&scope=account_email"
    )


def kakao_callback(request):
    rest_api_key = os.environ.get("SOCIAL_AUTH_KAKAO_CLIENT_ID")
    code = request.GET.get("code")
    redirect_uri = KAKAO_CALLBACK_URI
    """
    Access Token Request
    """
    token_req = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={redirect_uri}&code={code}"
    )
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get("access_token")
    """
    Email Request
    """
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
    print(kakao_account)
    print(kakao_account["profile"].get("nickname"))
    email = kakao_account.get("email")
    """
    Signup or Signin Request
    """

    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse(
                {"err_msg": "email exists but not social user"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if social_user.provider != "kakao":
            return JsonResponse(
                {"err_msg": "no matching social type"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 기존에 Google로 가입된 유저
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}users/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signin"}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop("user", None)
        # return JsonResponse(accept_json)
        return redirect("http://127.0.0.1:5500/html/index.html")

    except User.DoesNotExist:
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}users/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signup"}, status=accept_status)
        # user의 무슨 정보를 가져오니...
        accept_json = accept.json()
        # print(accept_json)
        accept_json.pop("user", None)
        # return JsonResponse(accept_json)
        return redirect("http://127.0.0.1:5500/html/index.html")


class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI


NAVER_CALLBACK_URI = BASE_URL + "users/naver/callback/"


def naver_login(request):
    client_id = os.environ.get("SOCIAL_AUTH_NAVER_CLIENT_ID")
    return redirect(
        f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={client_id}&state=STATE_STRING&redirect_uri={NAVER_CALLBACK_URI}"
    )


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

    # return JsonResponse({"access_token":access_token})

    # access token으로 네이버 프로필 요청
    profile_request = requests.post(
        "https://openapi.naver.com/v1/nid/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()

    email = profile_json.get("response").get("email")

    if email is None:
        return JsonResponse(
            {"err_msg": "failed to get email"}, status=status.HTTP_400_BAD_REQUEST
        )

    # 받아온 네이버 계정으로 회원가입/로그인 시도
    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse(
                {"err_msg": "email exists but not social user"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if social_user.provider != "naver":
            return JsonResponse(
                {"err_msg": "no matching social type"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 기존에 Google로 가입된 유저
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}users/naver/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signin"}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop("user", None)
        # return JsonResponse(accept_json)
        return redirect("http://127.0.0.1:5500/html/index.html")

    except User.DoesNotExist:
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}users/naver/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signup"}, status=accept_status)
        # user의 무슨 정보를 가져오니...
        accept_json = accept.json()
        # print(accept_json)
        accept_json.pop("user", None)
        # return JsonResponse(accept_json)
        return redirect("http://127.0.0.1:5500/html/index.html")


class NaverLogin(SocialLoginView):
    adapter_class = naver_view.NaverOAuth2Adapter
    callback_url = NAVER_CALLBACK_URI
    client_class = OAuth2Client
