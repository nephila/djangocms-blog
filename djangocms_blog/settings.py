# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

MENU_TYPE_COMPLETE = 'complete'
MENU_TYPE_CATEGORIES = 'categories'
MENU_TYPE_POSTS = 'posts'
MENU_TYPE_NONE = 'none'


def get_setting(name):
    from django.conf import settings
    from django.utils.translation import ugettext_lazy as _
    from meta_mixin import settings as meta_settings

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
    MENU_TYPES = (
        (MENU_TYPE_COMPLETE, _('Categories and posts')),
        (MENU_TYPE_CATEGORIES, _('Categories only')),
        (MENU_TYPE_POSTS, _('Posts only')),
        (MENU_TYPE_NONE, _('None')),
    )
    SITEMAP_CHANGEFREQ_LIST = (
        ('always', _('always')),
        ('hourly', _('hourly')),
        ('daily', _('daily')),
        ('weekly', _('weekly')),
        ('monthly', _('monthly')),
        ('yearly', _('yearly')),
        ('never', _('never')),
    )
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

        'BLOG_PAGINATION': getattr(settings, 'BLOG_PAGINATION', 10),
        'BLOG_LATEST_POSTS': getattr(settings, 'BLOG_LATEST_POSTS', 5),
        'BLOG_POSTS_LIST_TRUNCWORDS_COUNT': getattr(
            settings, 'BLOG_POSTS_LIST_TRUNCWORDS_COUNT', 100
        ),
        'BLOG_MENU_TYPES': MENU_TYPES,
        'BLOG_TYPE': getattr(settings, 'BLOG_TYPE', 'Article'),
        'BLOG_TYPES': meta_settings.OBJECT_TYPES,
        'BLOG_FB_TYPE': getattr(settings, 'BLOG_FB_TYPE', 'Article'),
        'BLOG_FB_TYPES': getattr(settings, 'BLOG_FB_TYPES', meta_settings.FB_TYPES),
        'BLOG_FB_APPID': getattr(settings, 'BLOG_FB_APPID', meta_settings.FB_APPID),
        'BLOG_FB_PROFILE_ID': getattr(settings, 'BLOG_FB_PROFILE_ID', meta_settings.FB_PROFILE_ID),
        'BLOG_FB_PUBLISHER': getattr(settings, 'BLOG_FB_PUBLISHER', meta_settings.FB_PUBLISHER),
        'BLOG_FB_AUTHOR_URL': getattr(settings, 'BLOG_FB_AUTHOR_URL', 'get_author_url'),
        'BLOG_FB_AUTHOR': getattr(settings, 'BLOG_FB_AUTHOR', 'get_author_name'),
        'BLOG_TWITTER_TYPE': getattr(settings, 'BLOG_TWITTER_TYPE', 'summary'),
        'BLOG_TWITTER_TYPES': getattr(settings, 'BLOG_TWITTER_TYPES', meta_settings.TWITTER_TYPES),
        'BLOG_TWITTER_SITE': getattr(settings, 'BLOG_TWITTER_SITE', meta_settings.TWITTER_SITE),
        'BLOG_TWITTER_AUTHOR': getattr(settings, 'BLOG_TWITTER_AUTHOR', 'get_author_twitter'),
        'BLOG_GPLUS_TYPE': getattr(settings, 'BLOG_GPLUS_TYPE', 'Blog'),
        'BLOG_GPLUS_TYPES': getattr(settings, 'BLOG_GPLUS_TYPES', meta_settings.GPLUS_TYPES),
        'BLOG_GPLUS_AUTHOR': getattr(settings, 'BLOG_GPLUS_AUTHOR', 'get_author_gplus'),
        'BLOG_ENABLE_COMMENTS': getattr(settings, 'BLOG_ENABLE_COMMENTS', True),
        'BLOG_USE_ABSTRACT': getattr(settings, 'BLOG_USE_ABSTRACT', True),
        'BLOG_USE_PLACEHOLDER': getattr(settings, 'BLOG_USE_PLACEHOLDER', True),
        'BLOG_MULTISITE': getattr(settings, 'BLOG_MULTISITE', True),
        'BLOG_AUTHOR_DEFAULT': getattr(settings, 'BLOG_AUTHOR_DEFAULT', True),
        'BLOG_DEFAULT_PUBLISHED': getattr(settings, 'BLOG_DEFAULT_PUBLISHED', False),
        'BLOG_ADMIN_POST_FIELDSET_FILTER': getattr(
            settings, 'BLOG_ADMIN_POST_FIELDSET_FILTER', False),
        'BLOG_AVAILABLE_PERMALINK_STYLES': getattr(
            settings, 'BLOG_AVAILABLE_PERMALINK_STYLES', PERMALINKS
        ),
        'BLOG_PERMALINK_URLS': getattr(settings, 'BLOG_PERMALINK_URLS', PERMALINKS_URLS),
        'BLOG_DEFAULT_OBJECT_NAME': getattr(settings, 'BLOG_DEFAULT_OBJECT_NAME', 'Article'),

        'BLOG_AUTO_SETUP': getattr(settings, 'BLOG_AUTO_SETUP', True),
        'BLOG_AUTO_HOME_TITLE': getattr(settings, 'BLOG_AUTO_HOME_TITLE', 'Home'),
        'BLOG_AUTO_BLOG_TITLE': getattr(settings, 'BLOG_AUTO_BLOG_TITLE', 'Blog'),
        'BLOG_AUTO_APP_TITLE': getattr(settings, 'BLOG_AUTO_APP_TITLE', 'Blog'),
        'BLOG_AUTO_NAMESPACE': getattr(settings, 'BLOG_AUTO_NAMESPACE', 'Blog'),

        'BLOG_SITEMAP_PRIORITY_DEFAULT': getattr(settings, 'BLOG_SITEMAP_PRIORITY_DEFAULT', '0.5'),
        'BLOG_SITEMAP_CHANGEFREQ': getattr(
            settings, 'BLOG_SITEMAP_CHANGEFREQ', SITEMAP_CHANGEFREQ_LIST
        ),
        'BLOG_SITEMAP_CHANGEFREQ_DEFAULT': getattr(
            settings, 'BLOG_SITEMAP_CHANGEFREQ_DEFAULT', 'monthly'
        ),

        'BLOG_ENABLE_SEARCH': getattr(settings, 'BLOG_ENABLE_SEARCH', True),
        'BLOG_CURRENT_POST_IDENTIFIER': getattr(
            settings, 'BLOG_CURRENT_POST_IDENTIFIER', 'djangocms_post_current'),
        'BLOG_CURRENT_NAMESPACE': getattr(
            settings, 'BLOG_CURRENT_NAMESPACE', 'djangocms_post_current_config'),
        'BLOG_ENABLE_THROUGH_TOOLBAR_MENU': getattr(
            settings, 'BLOG_ENABLE_THROUGH_TOOLBAR_MENU', False),

        'BLOG_PLUGIN_MODULE_NAME': getattr(settings, 'BLOG_PLUGIN_MODULE_NAME', _('Blog')),
        'BLOG_LATEST_ENTRIES_PLUGIN_NAME': getattr(
            settings, 'BLOG_LATEST_ENTRIES_PLUGIN_NAME', _('Latest Blog Articles')),
        'BLOG_AUTHOR_POSTS_PLUGIN_NAME': getattr(
            settings, 'BLOG_AUTHOR_POSTS_PLUGIN_NAME', _('Author Blog Articles')),
        'BLOG_TAGS_PLUGIN_NAME': getattr(
            settings, 'BLOG_TAGS_PLUGIN_NAME', _('Tags')),
        'BLOG_CATEGORY_PLUGIN_NAME': getattr(
            settings, 'BLOG_CATEGORY_PLUGIN_NAME', _('Categories')),
        'BLOG_ARCHIVE_PLUGIN_NAME': getattr(
            settings, 'BLOG_ARCHIVE_PLUGIN_NAME', _('Archive')),

    }
    return default['BLOG_%s' % name]
