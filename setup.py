#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import djangocms_blog

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = djangocms_blog.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print('You probably want to also tag the version now:')
    print('  git tag -a %s -m "version %s"' % (version, version))
    print('  git push --tags')
    sys.exit()

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
        'django-parler>=1.2',
        'django-cms>=3.0',
        'django-taggit>=0.12.2',
        'django-filer',
        'pytz',
        'django-taggit-templatetags',
        'django-taggit-autosuggest',
        'djangocms-text-ckeditor',
        'cmsplugin-filer',
        'django-meta>=0.2',
        'django-meta-mixin>=0.1.1',
        'aldryn-apphooks-config',
    ],
    license='BSD',
    zip_safe=False,
    keywords='djangocms-blog, blog, django, wordpress, multilingual',
    test_suite='cms_helper.run',
    extras_require={
        'admin-enhancer': ['django-admin-enhancer'],
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Framework :: Django',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
