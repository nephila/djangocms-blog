==============
djangocms-blog
==============

.. image:: https://badge.fury.io/py/djangocms-blog.png
    :target: http://badge.fury.io/py/djangocms-blog
    
.. image:: https://travis-ci.org/yakky/djangocms-blog.png?branch=master
        :target: https://travis-ci.org/yakky/djangocms-blog

.. image:: https://pypip.in/d/djangocms-blog/badge.png
        :target: https://crate.io/packages/djangocms-blog?version=latest


A djangoCMS 3 blog application.

Still experimental and untested. You are welcome if you want to try it; if
you encounter any issue, please open an issue.

Documentation
-------------

No doc at the moment, sorry

Quickstart
----------

Install djangocms-blog::

    pip install djangocms-blog

Add ``djangocms_blog`` and its dependencies to INSTALLED_APPS::

    INSTALLED_APPS = [
        ...
        'filer',
        'parler',
        'taggit',
        'django_select2',
        'taggit_autosuggest',
        'djangocms_blog',
        ...
    ]

Then sync and migrate::

    $ python manage.py syncdb
    $ python manage.py migrate

For ``filer`` installationand configuration, please refer to http://django-filer.readthedocs.org

Features
--------

* Placeholder content editing
* Frontend editing using django CMS 3.0 frontend editor
* Multilingual support using django-parler

.. image:: https://d2weczhvl823v0.cloudfront.net/nephila/djangocms-blog/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

