from django.urls import re_path, path
from Valuaionsystem import consumers

websocket_urlpatterns = [
    re_path(r"ws/notifications/$", consumers.Notifications.as_asgi()),
]
