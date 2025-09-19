# routing.py
from django.urls import re_path, path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/classroom/$', consumers.ClassroomConsumer.as_asgi()),
    
    # Meeting room WebSocket  
    re_path(r'meeting/(?P<room_name>\w+)/$', consumers.MeetingConsumer.as_asgi()),
]