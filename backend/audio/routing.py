from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/asr/stream/(?P<dialect>\w+)/$', consumers.ASRStreamConsumer.as_asgi()),
]
