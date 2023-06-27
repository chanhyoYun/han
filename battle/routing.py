from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/battle/", consumers.BattleConsumer.as_asgi()),
]
