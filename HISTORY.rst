.. :changelog:

=======
History
=======

******************
0.8.10 (2017-01-02)
******************

* Fix error in get_absolute_url

******************
0.8.9 (2016-10-25)
******************

* Optimized querysets
* Fixed slug generation in wizard

******************
0.8.8 (2016-09-04)
******************

* Fixed issue with one migration
* Improved support for django CMS 3.4

******************
0.8.7 (2016-08-25)
******************

* Added support for django CMS 3.4
* Fixed issue with multisite support

******************
0.8.6 (2016-08-03)
******************

* Set the correct language during indexing

******************
0.8.5 (2016-06-26)
******************

* Fixed issues with ThumbnailOption migration under mysql.

******************
0.8.4 (2016-06-22)
******************

* Fixed issues with cmsplugin-filer 1.1.

******************
0.8.3 (2016-06-21)
******************

* Stricter filer dependency versioning.

******************
0.8.2 (2016-06-12)
******************

* Aldryn-only release. No code changes

******************
0.8.1 (2016-06-11)
******************

* Aldryn-only release. No code changes

******************
0.8.0 (2016-06-05)
******************

* Added django-knocker integration
* Changed the default value of date_published to null
* Cleared menu cache when changing menu layout in apphook config
* Fixed error with wizard multiple registration
* Made django CMS 3.2 the default version
* Fixed error with on_site filter
* Removed meta-mixin compatibility code
* Changed slug size to 255 chars
* Fixed pagination setting in list views
* Added API to set default sites if user has permission only for a subset of sites
* Added Aldryn integration

******************
0.7.0 (2016-03-19)
******************

* Make categories non required
* Fix tests with parler>=1.6
* Use all_languages_column to admin
* Add publish button
* Fix issues in migrations. Thanks @skirsdeda
* Fix selecting current menu item according to menu layout
* Fix some issues with haystack indexes
* Add support for moved ThumbnailOption
* Fix Django 1.9 issues
* Fix copy relations method in plugins
* Mitigate issue when apphook config can't be retrieved
* Mitigate issue when wizard double registration is triggered

******************
0.6.3 (2015-12-22)
******************

* Add BLOG_ADMIN_POST_FIELDSET_FILTER to filter admin fieldsets
* Ensure correct creation of full URL for canonical urls
* Move constants to settings
* Fix error when no config is found

******************
0.6.2 (2015-11-16)
******************

* Add app_config field to BlogLatestEntriesPlugin
* Fix __str__ plugins method
* Fix bug when selecting plugins template

******************
0.6.1 (2015-10-31)
******************

* Improve toolbar: add all languages for each post
* Improve toolbar: add per-apphook configurable changefreq, priority

******************
0.6.0 (2015-10-30)
******************

* Add support for django CMS 3.2 Wizard
* Add support for Apphook Config
* Add Haystack support
* Improved support for meta tags
* Improved admin
* LatestPostsPlugin tags field has been changed to a plain TaggableManager field.
  A migration is in place to move the data, but backup your data first.

******************
0.5.0 (2015-08-09)
******************

* Add support for Django 1.8
* Drop dependency on Django select2
* Code cleanups
* Enforce flake8 / isort checks
* Add categories menu
* Add option to disable the abstract

******************
0.4.0 (2015-03-22)
******************

* Fix Django 1.7 issues
* Fix dependencies on python 3 when using wheel packages
* Drop Django 1.5 support
* Fix various templates issues
* UX fixes in the admin

******************
0.3.1 (2015-01-07)
******************

* Fix page_name in template
* Set cascade to set null for post image and thumbnail options

******************
0.3.0 (2015-01-04)
******************

* Multisite support
* Configurable default author support
* Refactored settings
* Fix multilanguage issues
* Fix SEO fields length
* Post absolute url is generated from the title in any language if current is
  not available
* If djangocms-page-meta and djangocms-page-tags are installed, the relevant
  toolbar items are removed from the toolbar in the post detail view to avoid
  confusings page meta / tags with post ones
* Plugin API changed to filter out posts according to the request.
* Django 1.7 support
* Python 3.3 and 3.4 support

******************
0.2.0 (2014-09-24)
******************

* **INCOMPATIBLE CHANGE**: view names changed!
* Based on django parler 1.0
* Toolbar items contextual to the current page
* Add support for canonical URLs
* Add transifex support
* Add social tags via django-meta-mixin
* Per-post or site-wide comments enabling
* Simpler TextField-based content editing for simpler blogs
* Add support for custom user models

******************
0.1.0 (2014-03-06)
******************

* First experimental release
