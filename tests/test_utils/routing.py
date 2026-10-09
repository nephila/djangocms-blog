from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path, re_path

from djangocms_blog.liveblog.routing import channel_routing as djangocms_blog_routing
from knocker.routing import channel_routing as knocker_routing

# django CMS 3.x / channels 4.x + Django 5.x compatibility:
# channels.routing.URLRouter sets route.pattern._is_endpoint = False to enable prefix
# matching for nested routers, but Django 5.x's RoutePattern pre-computes _regex with
# the endpoint anchor (\Z) in __init__, so the _is_endpoint change has no effect.
# Using re_path avoids this: RegexPattern always uses search() when the regex has no
# trailing '$', giving proper prefix matching regardless of _is_endpoint.
application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter([path("knocker/", knocker_routing), re_path(r"^liveblog/", djangocms_blog_routing)])
        ),
    }
)
