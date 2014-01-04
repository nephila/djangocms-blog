# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

BLOG_IMAGE_THUMBNAIL_SIZE = {
    'size': '120x120',
    'crop': True,
    'upscale': False
}

BLOG_IMAGE_FULL_SIZE = {
    'size': '640x120',
    'crop': True,
    'upscale': False
}

BLOG_TAGCLOUD_MIN = 1
BLOG_TAGCLOUD_MAX = 10