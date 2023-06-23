from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/battle/(?P<room_name>\w+)/$", consumers.BattleConsumer.as_asgi()),
    # re_path(r"ws/notification/", consumers.NotificationConsumer.as_asgi()),
]
