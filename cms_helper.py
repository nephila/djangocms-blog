#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os

from tempfile import mkdtemp


def gettext(s): return s

HELPER_SETTINGS = dict(
    ROOT_URLCONF='tests.test_utils.urls',
    INSTALLED_APPS=[
        'filer',
        'parler',
        'meta',
        'easy_thumbnails',
        'django.contrib.sitemaps',
        'djangocms_text_ckeditor',
        'cmsplugin_filer_image',
        'taggit',
        'taggit_autosuggest',
        'aldryn_apphooks_config',
        'aldryn_search',
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
    FILE_UPLOAD_TEMP_DIR=mkdtemp(),
    SITE_ID=1,
    HAYSTACK_CONNECTIONS={
        'default': {}
    },
)

try:
    import cmsplugin_filer_image.migrations_django  # pragma: no cover # NOQA
    HELPER_SETTINGS[
        'MIGRATION_MODULES'
    ]['cmsplugin_filer_image'] = 'cmsplugin_filer_image.migrations_django'

except ImportError:
    pass

try:
    import admin_enhancer  # pragma: no cover # NOQA
    HELPER_SETTINGS['INSTALLED_APPS'].append('admin_enhancer')
except ImportError:
    pass

try:
    import meta_mixin  # pragma: no cover # NOQA
    HELPER_SETTINGS['INSTALLED_APPS'].append('meta_mixin')
except ImportError:
    pass

try:
    import knocker  # pragma: no cover # NOQA
    HELPER_SETTINGS['INSTALLED_APPS'].append('knocker')
    HELPER_SETTINGS['CHANNEL_LAYERS'] = {
        'default': {
            'BACKEND': 'asgiref.inmemory.ChannelLayer',
            'ROUTING': 'knocker.routing.channel_routing',
        },
    }
except ImportError:
    pass
os.environ['AUTH_USER_MODEL'] = 'tests.test_utils.CustomUser'


def run():
    from djangocms_helper import runner
    runner.cms('djangocms_blog')

if __name__ == '__main__':
    run()
