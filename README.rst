==============
djangocms-blog
==============

|Gitter| |PyPiVersion| |PyVersion| |Status| |TestCoverage| |CodeClimate| |License|

django CMS blog application - Support for multilingual posts, placeholders, social network meta tags and configurable apphooks.

Supported Django versions:

* Django 1.11, 2.0, 2.1

Supported django CMS versions:

* django CMS 3.5+

.. warning:: For Django<1.11, django CMS<3.5 versions support, use djangocms-blog 0.9.x.

.. warning:: Since 1.0 compatibility with cmsplugin-filer has been dropped.
             Check `cmsplugin-filer migration documentation`_

************
Installation
************

See `installation documentation`_

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

.. _installation documentation: http://djangocms-blog.readthedocs.io/en/latest/installation.html
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
