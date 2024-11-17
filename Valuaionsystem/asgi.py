from channels.auth import (
    AuthMiddlewareStack,
)
from channels.routing import ProtocolTypeRouter, URLRouter
from Valuaionsystem.routing import websocket_urlpatterns
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Valuaionsystem.settings')

application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
    }
)
