from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/tweet/(?P<keyword>\w+)/$', consumers.FeedConsumer.as_asgi()),
]