from django.urls import path
from crawled_data import views

urlpatterns = [
    path("naver/", views.NaverQuizView.as_view(), name="naver_quiz_view"),
    path("krdict/", views.KrDictQuizView.as_view(), name="krdict_quiz_view"),
]
