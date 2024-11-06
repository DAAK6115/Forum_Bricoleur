import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import posts.routing

# Définir DJANGO_SETTINGS_MODULE avant d'importer d'autres modules Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forum_bricoleur.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            posts.routing.websocket_urlpatterns
        )
    ),
})
