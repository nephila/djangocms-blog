# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from channels import route

from .consumers import liveblog_connect, liveblog_disconnect

channel_routing = [
    route(
        'websocket.connect', liveblog_connect,
        path=r'^/liveblog/(?P<apphook>[a-zA-Z0-9_-]+)/'
             r'(?P<lang>[a-zA-Z_-]+)/(?P<post>[a-zA-Z0-9_-]+)/$'
    ),
    route(
        'websocket.disconnect', liveblog_disconnect,
        path=r'^/liveblog/(?P<apphook>[a-zA-Z0-9_-]+)/'
             r'(?P<lang>[a-zA-Z_-]+)/(?P<post>[a-zA-Z0-9_-]+)/$'
    ),
]
