from optparse import OptionParser
import sys
from tempfile import mkdtemp
gettext = lambda s: s

try:
    from django.conf import settings

    settings.configure(
        DEBUG=True,
        THUMBNAIL_DEBUG=True,
        TEMPLATE_DEBUG=True,
        USE_TZ=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        TEMPLATE_CONTEXT_PROCESSORS=[
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'django.core.context_processors.i18n',
            'django.core.context_processors.debug',
            'django.core.context_processors.request',
            'django.core.context_processors.media',
            'django.core.context_processors.csrf',
            'cms.context_processors.cms_settings',
            'sekizai.context_processors.sekizai',
            'django.core.context_processors.static',
        ],
        MIDDLEWARE_CLASSES=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.middleware.locale.LocaleMiddleware',
            'django.middleware.doc.XViewMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.cache.FetchFromCacheMiddleware',
            'cms.middleware.language.LanguageCookieMiddleware',
            'cms.middleware.user.CurrentUserMiddleware',
            'cms.middleware.page.CurrentPageMiddleware',
            'cms.middleware.toolbar.ToolbarMiddleware',
        ],
        ROOT_URLCONF='tests.test_utils.urls',
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.admin',
            'django.contrib.contenttypes',
            'django.contrib.sites',
            'cms',
            'django_nose',
            'menus',
            'mptt',
            'sekizai',
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
            'tests.test_utils',
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
            'default': {
                'hide_untranslated': False,
            },
        },
        CMS_TEMPLATES=(
            ('page.html', 'page'),
        ),
        SITE_ID=1,
        NOSE_ARGS=['-s'],
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
        FILE_UPLOAD_TEMP_DIR=mkdtemp()
    )

    from django_nose import NoseTestSuiteRunner
except ImportError as e:
    print(e)
    raise ImportError('To fix this error, run: pip install -r requirements-test.txt')


def run_tests(*test_args):
    if not test_args:
        test_args = ['tests']

    # Run tests
    test_runner = NoseTestSuiteRunner(verbosity=1)

    failures = test_runner.run_tests(test_args)

    if failures:
        sys.exit(failures)


if __name__ == '__main__':
    parser = OptionParser()
    (options, args) = parser.parse_args()
    run_tests(*args)
