#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
import sys
from tempfile import mkdtemp


def gettext(s):
    return s


HELPER_SETTINGS = dict(
    ROOT_URLCONF='tests.test_utils.urls',
    INSTALLED_APPS=[
        'filer',
        'parler',
        'meta',
        'easy_thumbnails',
        'django.contrib.sitemaps',
        'djangocms_text_ckeditor',
        'taggit',
        'taggit_autosuggest',
        'aldryn_apphooks_config',
        'aldryn_search',
        'sortedm2m',
    ],
    LANGUAGE_CODE='en',
    LANGUAGES=(
        ('en', gettext('English')),
        ('fr', gettext('French')),
        ('it', gettext('Italiano')),
    ),
    CMS_LANGUAGES={
        1: [
            {
                'code': 'en',
                'name': gettext('English'),
                'public': True,
            },
            {
                'code': 'it',
                'name': gettext('Italiano'),
                'public': True,
            },
            {
                'code': 'fr',
                'name': gettext('French'),
                'public': True,
            },
        ],
        2: [
            {
                'code': 'en',
                'name': gettext('English'),
                'public': True,
            },
        ],
        'default': {
            'hide_untranslated': False,
        },
    },
    PARLER_LANGUAGES={
        1: (
            {'code': 'en'},
            {'code': 'it'},
            {'code': 'fr'},
        ),
        2: (
            {'code': 'en'},
        ),
        'default': {
            'fallbacks': ['en'],
            'hide_untranslated': False,
        }
    },
    MIGRATION_MODULES={},
    CMS_TEMPLATES=(
        ('blog.html', 'Blog template'),
    ),
    META_SITE_PROTOCOL='http',
    META_USE_SITES=True,
    META_SITE_DOMAIN='example.com',
    META_USE_OG_PROPERTIES=True,
    META_USE_TWITTER_PROPERTIES=True,
    META_USE_GOOGLEPLUS_PROPERTIES=True,
    THUMBNAIL_PROCESSORS=(
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        'filer.thumbnail_processors.scale_and_crop_with_subject_location',
        'easy_thumbnails.processors.filters',
    ),
    USE_TZ=True,
    TIME_ZONE='UTC',
    FILE_UPLOAD_TEMP_DIR=mkdtemp(),
    SITE_ID=1,
    HAYSTACK_CONNECTIONS={
        'default': {}
    },
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    BLOG_AUTO_SETUP=False,
    ALLOWED_HOSTS=['*'],
)

try:
    import cmsplugin_filer_image.migrations_django  # pragma: no cover # NOQA

    HELPER_SETTINGS[
        'MIGRATION_MODULES'
    ]['cmsplugin_filer_image'] = 'cmsplugin_filer_image.migrations_django'

except ImportError:
    pass

try:
    import knocker  # pragma: no cover # NOQA

    HELPER_SETTINGS['INSTALLED_APPS'].append('knocker')
    HELPER_SETTINGS['INSTALLED_APPS'].append('channels')
    HELPER_SETTINGS['INSTALLED_APPS'].append('djangocms_blog.liveblog', )
    HELPER_SETTINGS['CHANNEL_LAYERS'] = {
        'default': {
            'BACKEND': 'asgiref.inmemory.ChannelLayer',
            'ROUTING': 'tests.test_utils.routing.channel_routing',
        },
    }
except ImportError:
    pass
os.environ['AUTH_USER_MODEL'] = 'tests.test_utils.CustomUser'

if 'server' in sys.argv[:3]:
    HELPER_SETTINGS['BLOG_AUTO_SETUP'] = True


def run():
    from djangocms_helper import runner
    runner.cms('djangocms_blog')


def setup():
    from djangocms_helper import runner
    runner.setup('djangocms_blog', sys.modules[__name__], use_cms=True)


if __name__ == '__main__':
    run()
