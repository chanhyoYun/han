from django.urls import path
from quizzes import views

urlpatterns = [
    path("result/", views.QuizResultView.as_view(), name="quiz_result"),
    path("suggest/", views.QuizSuggestView.as_view(), name="quiz_suggest"),
    path("report/", views.QuizReportView.as_view(), name="quiz_report"),
]
