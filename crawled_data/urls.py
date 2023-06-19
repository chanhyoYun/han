from django.urls import path
from crawled_data import views

urlpatterns = [
    path("gen/", views.PuzzleCreateView.as_view(), name="puzzle_create_view"),
]
