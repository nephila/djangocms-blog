# -*- coding: utf-8 -*-

from django.conf import settings

BLOG_IMAGE_THUMBNAIL_SIZE = getattr(settings, 'BLOG_IMAGE_THUMBNAIL_SIZE', {
    'size': '120x120',
    'crop': True,
    'upscale': False
})

BLOG_IMAGE_FULL_SIZE = getattr(settings, 'BLOG_IMAGE_FULL_SIZE', {
    'size': '640x120',
    'crop': True,
    'upscale': False
})

BLOG_TAGCLOUD_MIN = getattr(settings, 'BLOG_TAGCLOUD_MIN', 1)
BLOG_TAGCLOUD_MAX = getattr(settings, 'BLOG_TAGCLOUD_MAX', 10)
BLOG_PAGINATION = getattr(settings, 'BLOG_PAGINATION', 10)
BLOG_LATEST_POSTS = getattr(settings, 'BLOG_LATEST_POSTS', 5)
BLOG_POSTS_LIST_TRUNCWORDS_COUNT = getattr(settings, 'BLOG_POSTS_LIST_TRUNCWORDS_COUNT', 100)
