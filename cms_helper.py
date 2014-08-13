# -*- coding: utf-8 -*-
from tempfile import mkdtemp
gettext = lambda s: s

HELPER_SETTINGS = {
        'NOSE_ARGS':['-s'],
        'ROOT_URLCONF':'tests.test_utils.urls',
        'INSTALLED_APPS':[
            'django_nose',
            'filer',
            'parler',
            'taggit',
            'meta',
            'meta_mixin',
            'easy_thumbnails',
            'djangocms_text_ckeditor',
            'cmsplugin_filer_image',
            'django_select2',
            'taggit_autosuggest',
            'djangocms_blog',
        ],
        'LANGUAGE_CODE':'en',
        'LANGUAGES':(
            ('en', gettext('English')),
            ('fr', gettext('French')),
            ('it', gettext('Italiano')),
        ),
        'CMS_LANGUAGES':{
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
            'default': {
                'hide_untranslated': False,
            },
        },
        'META_SITE_PROTOCOL':'http',
        'META_SITE_DOMAIN':'example.com',
        'META_USE_OG_PROPERTIES':True,
        'META_USE_TWITTER_PROPERTIES':True,
        'META_USE_GOOGLEPLUS_PROPERTIES':True,
        'THUMBNAIL_PROCESSORS':(
            'easy_thumbnails.processors.colorspace',
            'easy_thumbnails.processors.autocrop',
            'filer.thumbnail_processors.scale_and_crop_with_subject_location',
            'easy_thumbnails.processors.filters',
        ),
        'FILE_UPLOAD_TEMP_DIR':mkdtemp()

}