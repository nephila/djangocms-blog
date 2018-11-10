#!/usr/bin/env python
# -*- coding: utf-8 -*-
import djangocms_blog

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = djangocms_blog.__version__


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


setup(
    name='djangocms-blog',
    version=version,
    description='A djangoCMS 3 blog application',
    long_description=readme + '\n\n' + history,
    author='Iacopo Spalletti',
    author_email='i.spalletti@nephila.it',
    url='https://github.com/nephila/djangocms-blog',
    packages=[
        'djangocms_blog',
    ],
    include_package_data=True,
    install_requires=[
        'django-parler>=1.9',
        'django-cms>=3.4',
        'django-taggit>=0.12.2',
        'django-filer>=1.3',
        'pytz',
        'django-taggit-templatetags',
        'django-taggit-autosuggest',
        'djangocms-text-ckeditor>=3.5',
        'easy-thumbnails>=2.4.1',
        'django-meta>=1.4',
        'aldryn-apphooks-config>=0.4',
        'djangocms-apphook-setup',
        'django-sortedm2m',
        'lxml',
    ],
    extras_require={
        'search': ['aldryn-search'],
        'taggit-helpers': ['django-taggit-helpers']
    },
    license='BSD',
    zip_safe=False,
    keywords='djangocms-blog, blog, django, wordpress, multilingual',
    test_suite='cms_helper.run',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
