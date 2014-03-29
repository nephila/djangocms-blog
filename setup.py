# -*- coding: utf-8 -*-
#!/usr/bin/env python

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
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
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
        'django-parler>=1.0',
        'django-cms>=3.0c1',
        'django-taggit',
        'django-filer',
        'django-select2',
        'pytz',
        'django-taggit-templatetags',
        'django-taggit-autosuggest',
        'django-admin-enhancer',
    ],
    dependency_links=[
        'https://github.com/edoburu/django-parler/archive/cdd500bb28a234d870274e73cba9d7020f1ef0b1.zip#egg=django-parler-1.0',
    ],
    license="BSD",
    zip_safe=False,
    keywords='djangocms-blog',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
