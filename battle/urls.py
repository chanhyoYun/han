from django.urls import path
from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    # path("<str:room_name>/", views.room, name="room"),
    path("game/", views.GameView.as_view(), name="new_game_create"),
    path("game/<int:room_id>/", views.GameDetailView.as_view(), name="game_detail"),
]
