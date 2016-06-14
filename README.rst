==============
djangocms-blog
==============

.. image:: https://img.shields.io/pypi/v/djangocms-blog.svg?style=flat-square
    :target: https://pypi.python.org/pypi/djangocms-blog
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/djangocms-blog.svg?style=flat-square
    :target: https://pypi.python.org/pypi/djangocms-blog
    :alt: Monthly downloads

.. image:: https://img.shields.io/pypi/pyversions/djangocms-blog.svg?style=flat-square
    :target: https://pypi.python.org/pypi/djangocms-blog
    :alt: Python versions

.. image:: https://img.shields.io/travis/nephila/djangocms-blog.svg?style=flat-square
    :target: https://travis-ci.org/nephila/djangocms-blog
    :alt: Latest Travis CI build status

.. image:: https://img.shields.io/coveralls/nephila/djangocms-blog/master.svg?style=flat-square
    :target: https://coveralls.io/r/nephila/djangocms-blog?branch=master
    :alt: Test coverage

.. image:: https://img.shields.io/codecov/c/github/nephila/djangocms-blog/develop.svg?style=flat-square
    :target: https://codecov.io/github/nephila/djangocms-blog
    :alt: Test coverage

.. image:: https://codeclimate.com/github/nephila/djangocms-blog/badges/gpa.svg?style=flat-square
   :target: https://codeclimate.com/github/nephila/djangocms-blog
   :alt: Code Climate

django CMS blog application - Support for multilingual posts, placeholders, social network meta tags and configurable apphooks.

Supported Django versions:

* Django 1.8
* Django 1.9

Supported django CMS versions:

* django CMS 3.2+

.. warning:: Version 0.8 will be the last one supporting Python 2.6, Python 3.3,
             Django<1.8 and django CMS<3.2.

.. warning:: Starting from version 0.8, date_published is not set anymore
             when creating a post but rather when publishing.
             This does not change the overall behavior, but be warned if you
             expect it to be not null in custom code.

.. warning:: Version 0.6 changes the field of LatestPostsPlugin.tags field.
             A datamigration is in place to migrate the data, but check that
             works ok for your project before upgrading, as this might delete
             some relevant data.
             Some plugins have a broken tag management prior to 0.6, in case
             you have issues with tags, upgrade to latest version to have it fixed.

Features
--------

* Placeholder content editing
* Frontend editing using django CMS 3.x frontend editor
* Multilingual support using django-parler
* Support for Twitter cards, Open Graph and Google+ snippets meta tags
* Optional support for simpler TextField-based content editing
* Multisite support (posts can be visible in one or more Django sites on the
  same project)
* Per-Apphook configuration
* Configurable permalinks
* Configurable django CMS menu support
* Per-Apphook templates set
* Auto Apphook setup
* Django sitemap framework support
* Support for django CMS 3.2+ Wizard
* Haystack index support

Documentation
-------------

Check documentation at https://djangocms-blog.readthedocs.io/en/latest/

Known djangocms-blog websites
+++++++++++++++++++++++++++++

See DjangoPackages for an updated list https://www.djangopackages.com/packages/p/djangocms-blog/
