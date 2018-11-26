.. _settings:

###############
Global Settings
###############

* BLOG_IMAGE_THUMBNAIL_SIZE: Size of the main image when shown on the post
  lists; it's a dictionary with ``size``, ``crop`` and ``upscale`` keys;
  (default: ``{'size': '120x120', 'crop': True,'upscale': False}``)
* BLOG_IMAGE_FULL_SIZE: Size of the main image when shown on the post
  detail; it's a dictionary with ``size``, ``crop`` and ``upscale`` keys;
  (default: ``{'size': '640x120', 'crop': True,'upscale': False}``)
* BLOG_PAGINATION: Number of post per page; (default: ``10``)
* BLOG_MENU_EMPTY_CATEGORIES: Flag to show / hide categories without posts
  attached from the menu; (default: ``True``)
* BLOG_LATEST_POSTS: Default number of post in the **Latest post** plugin;
  (default: ``5``)
* BLOG_POSTS_LIST_TRUNCWORDS_COUNT: Default number of words shown for
  abstract in the post list; (default: ``100``)
* BLOG_TYPE: Generic type for the post object; (default: ``Article``)
* BLOG_TYPES: Choices of available blog types;
  (default: to ``META_OBJECT_TYPES`` defined in `django-meta settings`_)
* BLOG_FB_TYPE: Open Graph type for the post object; (default: ``Article``)
* BLOG_FB_TYPES: Choices of available blog types;
  (default: to ``META_FB_TYPES`` defined in `django-meta settings`_)
* BLOG_FB_APPID: Facebook Application ID
* BLOG_FB_PROFILE_ID: Facebook profile ID of the post author
* BLOG_FB_PUBLISHER: Facebook URL of the blog publisher
* BLOG_FB_AUTHOR_URL: Facebook profile URL of the post author
* BLOG_FB_AUTHOR: Facebook profile URL of the post author
* BLOG_TWITTER_TYPE: Twitter Card type for the post object;
  (default: ``Summary``)
* BLOG_TWITTER_TYPES: Choices of available blog types for twitter;
  (default: to ``META_TWITTER_TYPES`` defined in `django-meta settings`_)
* BLOG_TWITTER_SITE: Twitter account of the site
* BLOG_TWITTER_AUTHOR: Twitter account of the post author
* BLOG_GPLUS_TYPE: Google+ Snippet type for the post object;
  (default: ``Blog``)
* BLOG_GPLUS_TYPES: Choices of available blog types for twitter;
  (default: to ``META_GPLUS_TYPES`` defined in `django-meta settings`_)
* BLOG_GPLUS_AUTHOR: Google+ account of the post author
* BLOG_ENABLE_COMMENTS: Whether to enable comments by default on posts;
  while ``djangocms_blog`` does not ship any comment system, this flag
  can be used to control the chosen comments framework; (default: ``True``)
* BLOG_USE_ABSTRACT: Use an abstract field for the post; if ``False``
  no abstract field is available for every post; (default: ``True``)
* BLOG_USE_PLACEHOLDER: Post content is managed via placeholder;
  if ``False`` a simple HTMLField is used; (default: ``True``)
* BLOG_USE_RELATED: Enable related posts to link one post to others;
  (default: ``True``)
* BLOG_MULTISITE: Add support for multisite setup; (default: ``True``)
* BLOG_AUTHOR_DEFAULT: Use a default if not specified; if set to ``True`` the
  current user is set as the default author, if set to ``False`` no default
  author is set, if set to a string the user with the provided username is
  used; (default: ``True``)
* BLOG_DEFAULT_PUBLISHED: If posts are marked as published by default;
  (default: ``False``)
* BLOG_ADMIN_POST_FIELDSET_FILTER: Callable function to change(add or filter)
  fields to fieldsets for admin post edit form; (default: ``False``). Function simple example::


    def fieldset_filter_function(fsets, request, obj=None):
        if request.user.groups.filter(name='Editor').exists():
            fsets[1][1]['fields'][0].append('author')  # adding 'author' field if user is Editor
        return fsets


* BLOG_AVAILABLE_PERMALINK_STYLES: Choices of permalinks styles;
* BLOG_PERMALINK_URLS: URLConf corresponding to
  BLOG_AVAILABLE_PERMALINK_STYLES;
* BLOG_URLCONF: Apphoo URLConf; (default: ``'djangocms_blog.urls'``);
* BLOG_DEFAULT_OBJECT_NAME: Default name for Blog item (used in django CMS Wizard);
* BLOG_AUTO_SETUP: Enable the blog **Auto setup** feature; (default: ``True``)
* BLOG_AUTO_HOME_TITLE: Title of the home page created by **Auto setup**;
  (default: ``Home``)
* BLOG_AUTO_BLOG_TITLE: Title of the blog page created by **Auto setup**;
  (default: ``Blog``)
* BLOG_AUTO_APP_TITLE: Title of the ``BlogConfig`` instance created by
  **Auto setup**; (default: ``Blog``)
* BLOG_SITEMAP_PRIORITY_DEFAULT: Default priority for sitemap items; (default: ``0.5``)
* BLOG_SITEMAP_CHANGEFREQ: List for available changefreqs for sitemap items; (default: **always**,
  **hourly**, **daily**, **weekly**, **monthly**, **yearly**, **never**)
* BLOG_SITEMAP_CHANGEFREQ_DEFAULT: Default changefreq for sitemap items; (default: ``monthly``)
* BLOG_CURRENT_POST_IDENTIFIER: Current post identifier in request (default ``djangocms_post_current``)
* BLOG_CURRENT_NAMESPACE: Current post config identifier in request  (default: ``djangocms_post_current_config``)
* BLOG_ENABLE_THROUGH_TOOLBAR_MENU: Is the toolbar menu throught whole all applications (default: ``False``)
* BLOG_PLUGIN_MODULE_NAME: Blog plugin module name (default: ``Blog``)
* BLOG_LATEST_ENTRIES_PLUGIN_NAME: Blog latest entries plugin name (default: ``Latest Blog Articles``)
* BLOG_AUTHOR_POSTS_PLUGIN_NAME: Blog author posts plugin name (default: ``Author Blog Articles``)
* BLOG_TAGS_PLUGIN_NAME: Blog tags plugin name (default: ``Tags``)
* BLOG_CATEGORY_PLUGIN_NAME: Blog categories plugin name (default: ``Categories``)
* BLOG_ARCHIVE_PLUGIN_NAME: Blog archive plugin name (default: ``Archive``)
* BLOG_FEED_CACHE_TIMEOUT: Cache timeout for RSS feeds
* BLOG_FEED_INSTANT_ITEMS: Number of items in Instant Article feed
* BLOG_FEED_LATEST_ITEMS: Number of items in latest items feed
* BLOG_FEED_TAGS_ITEMS: Number of items in per tags feed
* BLOG_PLUGIN_TEMPLATE_FOLDERS: (Sub-)folder from which the plugin templates are loaded. The default folder is ``plugins``. It goes into the ``djangocms_blog`` template folder (or, if set, the folder named in the app hook). This allows, e.g., different templates for showing a post list as tables, columns, ... . New templates have the same names as the standard templates in the ``plugins`` folder (``latest_entries.html``, ``authors.html``, ``tags.html``, ``categories.html``, ``archive.html``). Default behavior corresponds to this setting being ``( ("plugins", _("Default template") )``. To add new templates add to this setting, e.g., ``('timeline', _('Vertical timeline') )``.
* BLOG_META_DESCRIPTION_LENGTH: Maximum length for the Meta description field (default: ``320``)
* BLOG_META_TITLE_LENGTH: Maximum length for the Meta title field (default: ``70``)
* BLOG_ABSTRACT_CKEDITOR: Configuration for the CKEditor of the abstract field (as per https://github.com/divio/djangocms-text-ckeditor/#customizing-htmlfield-editor)
* BLOG_POST_TEXT_CKEDITOR: Configuration for the CKEditor of the post content field

******************
Read-only settings
******************

* BLOG_MENU_TYPES: Available structures of the Blog menu; (default list **Posts and Categories**,
  **Categories only**, **Posts only**, **None**)
* BLOG_MENU_TYPE: Structure of the Blog menu;
  (default: ``Posts and Categories``)


********************
Per-Apphook settings
********************

The following settings can be configured for each ``Apphook config``: the settings above will
be used as defaults.

* application title: Free text title that can be used as title in templates;
* object name: Free text label for Blog items in django CMS Wizard;
* Post published by default: Per-Apphook setting for BLOG_DEFAULT_PUBLISHED;
* Permalink structure: Per-Apphook setting for
  BLOG_AVAILABLE_PERMALINK_STYLES;
* Use placeholder and plugins for article body: Per-Apphook setting for
  BLOG_USE_PLACEHOLDER;
* Use abstract field: Per-Apphook setting for BLOG_USE_ABSTRACT;
* Enable related posts: Per-Apphook setting for BLOG_USE_RELATED;
* Set author: Per-Apphook setting for BLOG_AUTHOR_DEFAULT;
* Paginate sizePer-Apphook setting for BLOG_PAGINATION;
* Template prefix: Alternative directory to load the blog templates from;
* Menu structure: Per-Apphook setting for BLOG_MENU_TYPE
* Show empty categories in menu: Per-Apphook setting for BLOG_MENU_EMPTY_CATEGORIES
* Sitemap changefreq: Per-Apphook setting for BLOG_SITEMAP_CHANGEFREQ_DEFAULT
* Sitemap priority: Per-Apphook setting for BLOG_SITEMAP_PRIORITY_DEFAULT
* Object type: Per-Apphook setting for BLOG_TYPE
* Facebook type: Per-Apphook setting for BLOG_FB_TYPE
* Facebook application ID: Per-Apphook setting for BLOG_FB_APP_ID
* Facebook profile ID: Per-Apphook setting for BLOG_FB_PROFILE_ID
* Facebook page URL: Per-Apphook setting for BLOG_FB_PUBLISHER
* Facebook author URL: Per-Apphook setting for BLOG_AUTHOR_URL
* Facebook author: Per-Apphook setting for BLOG_AUTHOR
* Twitter type: Per-Apphook setting for BLOG_TWITTER_TYPE
* Twitter site handle: Per-Apphook setting for BLOG_TWITTER_SITE
* Twitter author handle: Per-Apphook setting for BLOG_TWITTER_AUTHOR
* Google+ type: Per-Apphook setting for BLOG_GPLUS_TYPE
* Google+ author name: Per-Apphook setting for BLOG_GPLUS_AUTHOR
* Send notifications on post publish: Send desktop notifications when a post is published
* Send notifications on post update: Send desktop notifications when a post is updated


.. _django-meta settings: https://github.com/nephila/django-meta#settings
