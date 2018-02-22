==============
djangocms-blog
==============

|Gitter| |PyPiVersion| |PyVersion| |Status| |TestCoverage| |CodeClimate| |License|

django CMS blog application - Support for multilingual posts, placeholders, social network meta tags and configurable apphooks.

Supported Django versions:

* Django 1.8
* Django 1.9
* Django 1.10
* Django 1.11

Supported django CMS versions:

* django CMS 3.2+

.. warning:: Strict dependency on aldryn-search, haystack has been dropped. Install
             them separately to enable full text search support. See `installation docs`_
             for details.

.. warning:: Version 0.8 will be the last one supporting Python 2.6, Python 3.3,
             Django<1.8 and django CMS<3.2.

.. warning:: Starting from version 0.8, date_published is not set anymore
             when creating a post but rather when publishing.
             This does not change the overall behavior, but be warned if you
             expect it to be not null in custom code.

*****************************************
Upgrading cmsplugin-filer from 1.0 to 1.1
*****************************************

Due to changes in cmsplugin-filer/filer which moved ``ThumbnailOption`` model from the
former to the latter, ``djangocms-blog`` must be migrated as well.

Migrating cmsplugin-filer to 1.1 and djangocms-blog up to 0.8.4
===============================================================

If you have djangocms-blog up to 0.8.4 (included) installed or you are upgrading from a previous
djangocms-blog version together with cmsplugin-filer upgrade, you can just apply the migrations::

    pip install cmsplugin-filer==1.1.3 django-filer==1.2.7 djangocms-blog==0.8.4
    python manage.py migrate

Migrating cmsplugin-filer to 1.1 and djangocms-blog 0.8.5+
==========================================================

If you already a djangocms-blog 0.8.5+ up to 0.8.11, upgrade to 0.8.11, then
you have to de-apply some blog migrations when doing the upgrade::

    pip install djangocms-blog==0.8.11
    python manage.py migrate djangocms_blog 0017 ## reverse for these migration is a noop
    pip install cmsplugin-filer==1.1.3 django-filer==1.2.7
    python manage.py migrate

After this step you can upgrade to 0.8.12::

    pip install djangocms-blog==0.8.12

.. note:: de-apply migration **before** upgrading cmsplugin-filer. If running before upgrade, the
          backward migration won't alter anything on the database, and it will just allow the code
          to migrate ``ThumbnailOption`` from cmsplugin-filer to filer

.. note:: If you upgrade in a Django 1.10 environment, be sure to upgrade both packages
          at the same time to allow correct migration dependencies to be evaluated.

Installing djangocms-blog in an existing project with Django 1.10
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If your project has cmsplugin-filer 1.1+ already installed and it uses Django 1.10,
install djangocms-blog 0.8.12 (and above)::

    pip install djangocms-blog==0.8.12

********
Features
********

* Placeholder content editing
* Frontend editing using django CMS 3.x frontend editor
* Multilingual support using django-parler
* Twitter cards, Open Graph and Google+ snippets meta tags
* Optional simpler TextField-based content editing
* Multisite (posts can be visible in one or more Django sites on the same project)
* Per-Apphook configuration
* Configurable permalinks
* Configurable django CMS menu
* Per-Apphook templates set
* Auto Apphook setup
* Django sitemap framework
* django CMS 3.2+ Wizard
* Haystack index
* Desktop notifications
* Liveblog

*****************************
Known djangocms-blog websites
*****************************

See DjangoPackages for an updated list https://www.djangopackages.com/packages/p/djangocms-blog/


.. _installation docs: http://djangocms-blog.readthedocs.io/en/latest/installation.html



.. |Gitter| image:: https://img.shields.io/badge/GITTER-join%20chat-brightgreen.svg?style=flat-square
    :target: https://gitter.im/nephila/applications
    :alt: Join the Gitter chat

.. |PyPiVersion| image:: https://img.shields.io/pypi/v/djangocms-blog.svg?style=flat-square
    :target: https://pypi.python.org/pypi/djangocms-blog
    :alt: Latest PyPI version

.. |PyVersion| image:: https://img.shields.io/pypi/pyversions/djangocms-blog.svg?style=flat-square
    :target: https://pypi.python.org/pypi/djangocms-blog
    :alt: Python versions

.. |Status| image:: https://img.shields.io/travis/nephila/djangocms-blog.svg?style=flat-square
    :target: https://travis-ci.org/nephila/djangocms-blog
    :alt: Latest Travis CI build status

.. |TestCoverage| image:: https://img.shields.io/coveralls/nephila/djangocms-blog/master.svg?style=flat-square
    :target: https://coveralls.io/r/nephila/djangocms-blog?branch=master
    :alt: Test coverage

.. |License| image:: https://img.shields.io/github/license/nephila/djangocms-blog.svg?style=flat-square
   :target: https://pypi.python.org/pypi/djangocms-blog/
    :alt: License

.. |CodeClimate| image:: https://codeclimate.com/github/nephila/djangocms-blog/badges/gpa.svg?style=flat-square
   :target: https://codeclimate.com/github/nephila/djangocms-blog
   :alt: Code Climate
