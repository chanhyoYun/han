from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users.views import CustomTokenObtainPairView
from users import views, social

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", views.UserView.as_view(), name="signup"),
    path("<int:user_id>/", views.UserDetailView.as_view(), name="users_id"),
    path(
        "achieve/<int:achieve_id>/", views.AchievementView.as_view(), name="achievement"
    ),
    path(
        "verify/<str:uidb64>/<str:token>/",
        views.EmailVerifyView.as_view(),
        name="email_verify_view",
    ),
    path("reset/", views.PasswordResetView.as_view(), name="password_reset_view"),
    path("ranking/", views.RankingView.as_view(), name="ranking"),
    # 구글 소셜로그인
    path("google/login/", social.google_login, name="google_login"),
    path("google/callback/", social.google_callback, name="google_callback"),
    path(
        "google/login/finish/",
        social.GoogleLogin.as_view(),
        name="google_login_todjango",
    ),
    # 카카오 소셜 로그인
    path("kakao/login/", social.kakao_login, name="kakao_login"),
    path("kakao/callback/", social.kakao_callback, name="kakao_callback"),
    path(
        "kakao/login/finish/", social.KakaoLogin.as_view(), name="kakao_login_todjango"
    ),
    # 네이버 소셜 로그인
    path("naver/login/", social.naver_login, name="naver_login"),
    path("naver/callback/", social.naver_callback, name="naver_callback"),
    path(
        "naver/login/finish/", social.NaverLogin.as_view(), name="naver_login_todjango"
    ),
]
