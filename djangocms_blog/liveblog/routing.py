from channels.routing import URLRouter
from django.urls import path

from .consumers import LiveblogConsumer

channel_routing = URLRouter([path("<str:apphook>/<str:lang>/<str:post>/", LiveblogConsumer)])
