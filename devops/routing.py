#####routing.py#####

from channels.routing import ProtocolTypeRouter,URLRouter
from inst.urls import websocket_url

application = ProtocolTypeRouter({
    "websocket":URLRouter(
        websocket_url
    ),
})