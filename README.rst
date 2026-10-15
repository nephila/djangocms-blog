==============
djangocms-blog
==============

|Gitter| |PyPiVersion| |PyVersion| |GAStatus| |TestCoverage| |CodeClimate| |License|

django CMS blog application - Support for multilingual posts, placeholders, social network meta tags and configurable apphooks.

Compatibility matrix:

============ ========= =====================
Python       Django    django CMS
============ ========= =====================
3.9 – 3.11   3.2       3.9
3.9 – 3.11   4.1       3.11
3.9 – 3.12   4.2       3.11
3.10 – 3.12  5.0       4.x (>= 4.0, < 5.0)
3.10 – 3.13  5.1, 5.2  4.x (>= 4.0, < 5.0)
============ ========= =====================

************
Installation
************

See `installation documentation`_

When running on django CMS 4.x, add ``CMS_CONFIRM_VERSION4 = True`` to your
Django settings — django CMS 4 requires the host project to opt in explicitly.

********
Features
********

See `features documentation`_  for all the features details

* Support for `django-app-enabler`_ autoconfiguration.
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
.. _django-app-enabler: https://github.com/nephila/django-app-enabler


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
