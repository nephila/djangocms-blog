# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from channels import include

from djangocms_blog.liveblog.routing import channel_routing as djangocms_blog_routing
from knocker.routing import channel_routing as knocker_routing

channel_routing = [
    include(djangocms_blog_routing, path=r'^/liveblog'),
    include(knocker_routing, path=r'^/knocker'),
]
