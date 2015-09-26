# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals


def get_setting(name):
    from django.conf import settings
    from django.utils.translation import ugettext_lazy as _
    from meta_mixin import settings as meta_settings

    OBJECT_TYPES = (
        ('Article', _('Article')),
        ('Website', _('Website')),
    )
    BLOG_TYPES = getattr(settings, 'BLOG_TYPES', OBJECT_TYPES)

    PERMALINKS = (
        ('full_date', _('Full date')),
        ('short_date', _('Year /  Month')),
        ('category', _('Category')),
        ('slug', _('Just slug')),
    )
    PERMALINKS_URLS = {
        'full_date': r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>\w[-\w]*)/$',
        'short_date': r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>\w[-\w]*)/$',
        'category': r'^(?P<category>\w[-\w]*)/(?P<slug>\w[-\w]*)/$',
        'slug': r'^(?P<slug>\w[-\w]*)/$',
    }

    default = {
        'BLOG_IMAGE_THUMBNAIL_SIZE': getattr(settings, 'BLOG_IMAGE_THUMBNAIL_SIZE', {
            'size': '120x120',
            'crop': True,
            'upscale': False
        }),

        'BLOG_IMAGE_FULL_SIZE': getattr(settings, 'BLOG_IMAGE_FULL_SIZE', {
            'size': '640x120',
            'crop': True,
            'upscale': False
        }),

        'BLOG_TAGCLOUD_MIN': getattr(settings, 'BLOG_TAGCLOUD_MIN', 1),
        'BLOG_TAGCLOUD_MAX': getattr(settings, 'BLOG_TAGCLOUD_MAX', 10),
        'BLOG_PAGINATION': getattr(settings, 'BLOG_PAGINATION', 10),
        'BLOG_LATEST_POSTS': getattr(settings, 'BLOG_LATEST_POSTS', 5),
        'BLOG_POSTS_LIST_TRUNCWORDS_COUNT': getattr(
            settings, 'BLOG_POSTS_LIST_TRUNCWORDS_COUNT', 100
        ),
        'BLOG_TYPE': getattr(settings, 'BLOG_TYPE', 'Article'),
        'BLOG_TYPES': BLOG_TYPES,
        'BLOG_FB_TYPE': getattr(settings, 'BLOG_FB_TYPE', 'Article'),
        'BLOG_FB_TYPES': getattr(settings, 'BLOG_FB_TYPES', BLOG_TYPES),
        'BLOG_FB_APPID': getattr(settings, 'BLOG_FB_APPID', meta_settings.FB_APPID),
        'BLOG_FB_PROFILE_ID': getattr(settings, 'BLOG_FB_PROFILE_ID', meta_settings.FB_PROFILE_ID),
        'BLOG_FB_PUBLISHER': getattr(settings, 'BLOG_FB_PUBLISHER', meta_settings.FB_PUBLISHER),
        'BLOG_FB_AUTHOR_URL': getattr(settings, 'BLOG_FB_AUTHOR_URL', 'get_author_url'),
        'BLOG_FB_AUTHOR': getattr(settings, 'BLOG_FB_AUTHOR', 'get_author_name'),
        'BLOG_TWITTER_TYPE': getattr(settings, 'BLOG_TWITTER_TYPE', 'Summary'),
        'BLOG_TWITTER_TYPES': getattr(settings, 'BLOG_TWITTER_TYPES', BLOG_TYPES),
        'BLOG_TWITTER_SITE': getattr(settings, 'BLOG_TWITTER_SITE', meta_settings.TWITTER_SITE),
        'BLOG_TWITTER_AUTHOR': getattr(settings, 'BLOG_TWITTER_AUTHOR', 'get_author_twitter'),
        'BLOG_GPLUS_TYPE': getattr(settings, 'BLOG_GPLUS_SCOPE_CATEGORY', 'Blog'),
        'BLOG_GPLUS_TYPES': getattr(settings, 'BLOG_GPLUS_TYPES', BLOG_TYPES),
        'BLOG_GPLUS_AUTHOR': getattr(settings, 'BLOG_GPLUS_AUTHOR', 'get_author_gplus'),
        'BLOG_ENABLE_COMMENTS': getattr(settings, 'BLOG_ENABLE_COMMENTS', True),
        'BLOG_USE_ABSTRACT': getattr(settings, 'BLOG_USE_ABSTRACT', True),
        'BLOG_USE_PLACEHOLDER': getattr(settings, 'BLOG_USE_PLACEHOLDER', True),
        'BLOG_MULTISITE': getattr(settings, 'BLOG_MULTISITE', True),
        'BLOG_AUTHOR_DEFAULT': getattr(settings, 'BLOG_AUTHOR_DEFAULT', True),
        'BLOG_DEFAULT_PUBLISHED': getattr(settings, 'BLOG_DEFAULT_PUBLISHED', False),
        'BLOG_AVAILABLE_PERMALINK_STYLES': getattr(settings, 'BLOG_AVAILABLE_PERMALINK_STYLES', PERMALINKS),  # NOQA
        'BLOG_PERMALINK_URLS': getattr(settings, 'BLOG_PERMALINK_URLS', PERMALINKS_URLS),
    }
    return default['BLOG_%s' % name]
