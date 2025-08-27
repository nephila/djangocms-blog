from tempfile import mkdtemp


def gettext(s):
    return s


#
SECRET_KEY = "utterly-secret"
ROOT_URLCONF = "tests.test_utils.urls"
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "tests.test_utils",
    "tests.media_app",
    "filer",
    "easy_thumbnails",
    "parler",
    "meta",
    "cms",
    "menus",
    "treebeard",
    "sekizai",
    "djangocms_text",
    "djangocms_blog",
    "taggit",
    "taggit_autosuggest",
    "djangocms_video",
    "sortedm2m",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "cms.middleware.user.CurrentUserMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
    "cms.middleware.toolbar.ToolbarMiddleware",
    "cms.middleware.language.LanguageCookieMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "sekizai.context_processors.sekizai",
                "cms.context_processors.cms_settings",
            ],
        },
    },
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
LANGUAGE_CODE = "en"
LANGUAGES = (("en", gettext("English")), ("fr", gettext("French")), ("it", gettext("Italiano")))
CMS_LANGUAGES = {
    1: [
        {"code": "en", "name": gettext("English"), "public": True},
        {"code": "it", "name": gettext("Italiano"), "public": True},
        {"code": "fr", "name": gettext("French"), "public": True},
    ],
    2: [{"code": "en", "name": gettext("English"), "public": True}],
    "default": {"hide_untranslated": False},
}
PARLER_LANGUAGES = {
    1: ({"code": "en"}, {"code": "it"}, {"code": "fr"}),
    2: ({"code": "en"},),
    "default": {"fallbacks": ["en"], "hide_untranslated": False},
}
CMS_TEMPLATES = (("blog.html", "Blog template"),)
META_SITE_PROTOCOL = "http"
META_USE_SITES = True
META_SITE_DOMAIN = "example.com"
META_USE_OG_PROPERTIES = True
META_USE_TWITTER_PROPERTIES = True
META_USE_SCHEMAORG_PROPERTIES = True
THUMBNAIL_PROCESSORS = (
    "easy_thumbnails.processors.colorspace",
    "easy_thumbnails.processors.autocrop",
    "filer.thumbnail_processors.scale_and_crop_with_subject_location",
    "easy_thumbnails.processors.filters",
)
USE_TZ = True
TIME_ZONE = "UTC"
FILE_UPLOAD_TEMP_DIR = mkdtemp()
SITE_ID = 1
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
BLOG_AUTO_SETUP = False
DEBUG = False
CMS_CONFIRM_VERSION4 = True

AUTH_USER_MODEL = "test_utils.CustomUser"

STATIC_URL = "/static/"
