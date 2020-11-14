==============
djangocms-blog
==============

|Gitter| |PyPiVersion| |PyVersion| |GAStatus| |TestCoverage| |CodeClimate| |License|

django CMS blog application - Support for multilingual posts, placeholders, social network meta tags and configurable apphooks.

Supported Django versions:

* Django 2.2, 3.0, 3.1

Supported django CMS versions:

* django CMS 3.7, 3.8+

.. warning:: For Django<2.2, django CMS<3.7 versions support, use djangocms-blog 1.1x.

.. warning:: Version 1.2 introduce a breaking change for customized ``BLOG_PERMALINK_URLS``.
             Check the `permalinks`_ documentation for update information.

************
Installation
************

See `installation documentation`_

********
Features
********

See `features documentation`_  for all the features details

* Placeholder content editing
* Frontend editing using django CMS frontend editor
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
* django CMS Wizard integration
* Haystack index
* Desktop notifications
* Liveblog

*****************************
Known djangocms-blog websites
*****************************

See DjangoPackages for an updated list https://www.djangopackages.com/packages/p/djangocms-blog/

.. _features documentation: http://djangocms-blog.readthedocs.io/en/latest/features/
.. _installation documentation: http://djangocms-blog.readthedocs.io/en/latest/installation.html
.. _permalinks: http://djangocms-blog.readthedocs.io/en/latest/features/permalinks.html
.. _cmsplugin-filer migration documentation: http://djangocms-blog.readthedocs.io/en/latest/cmsplugin_filer.html


.. |Gitter| image:: https://img.shields.io/badge/GITTER-join%20chat-brightgreen.svg?style=flat-square
    :target: https://gitter.im/nephila/applications
    :alt: Join the Gitter chat

.. |PyPiVersion| image:: https://img.shields.io/pypi/v/djangocms-blog.svg?style=flat-square
    :target: https://pypi.python.org/pypi/djangocms-blog
    :alt: Latest PyPI version

.. |PyVersion| image:: https://img.shields.io/pypi/pyversions/djangocms-blog.svg?style=flat-square
    :target: https://pypi.python.org/pypi/djangocms-blog
    :alt: Python versions

.. |GAStatus| image:: https://github.com/nephila/djangocms-blog/workflows/Tox%20tests/badge.svg
    :target: https://github.com/nephila/djangocms-blog
    :alt: Latest CI build status

.. |TestCoverage| image:: https://img.shields.io/coveralls/nephila/djangocms-blog/master.svg?style=flat-square
    :target: https://coveralls.io/r/nephila/djangocms-blog?branch=master
    :alt: Test coverage

.. |License| image:: https://img.shields.io/github/license/nephila/djangocms-blog.svg?style=flat-square
   :target: https://pypi.python.org/pypi/djangocms-blog/
    :alt: License

.. |CodeClimate| image:: https://codeclimate.com/github/nephila/djangocms-blog/badges/gpa.svg?style=flat-square
   :target: https://codeclimate.com/github/nephila/djangocms-blog
   :alt: Code Climate
