#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from tempfile import mkdtemp

gettext = lambda s: s

HELPER_SETTINGS = dict(
    ROOT_URLCONF='tests.test_utils.urls',
    INSTALLED_APPS=[
        'filer',
        'parler',
        'meta',
        'meta_mixin',
        'easy_thumbnails',
        'djangocms_text_ckeditor',
        'cmsplugin_filer_image',
        'taggit',
        'taggit_autosuggest',
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
            'fallback': 'en',
            'hide_untranslated': False,
        }
    },
    MIGRATION_MODULES={
        'cmsplugin_filer_image': 'cmsplugin_filer_image.migrations_django',
    },
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
    SITE_ID=1
)

try:
    import admin_enhancer  # pragma: no cover # NOQA
    HELPER_SETTINGS['INSTALLED_APPS'].append('admin_enhancer')
except ImportError:
    pass


def run():
    from djangocms_helper import runner
    runner.cms('djangocms_blog')

if __name__ == "__main__":
    run()
