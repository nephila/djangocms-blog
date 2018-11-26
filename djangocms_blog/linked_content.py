# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import re

import requests
from django.conf import settings


def vimeo_api(id, url):
    json = requests.get('http://vimeo.com/api/v2/video/%s.json' % id).json()
    return (json[0]['thumbnail_large'], json[0]['thumbnail_medium'])


def soundcloud_api(name, track, url):
    json = requests.get('http://api.soundcloud.com/resolve?client_id='
                        '%(client_id)s&'
                        'url=https://soundcloud.com/%(name)s/%(track)s' %
                        {
                            'client_id':
                                getattr(settings, 'SOUNDCLOUD_APIKEY',
                                        'LvWovRaJZlWCHql0bISuum8Bd2KX79mb'),
                            'name': name,
                            'track': track,
                         }).json()
    thumbnail = json['waveform_url']
    if 'artwork_url' in json and json['artwork_url']:
        thumbnail = json['artwork_url'].replace('large.jpg', 'crop.jpg')
    return (json['waveform_url'], thumbnail)


'''
    patterns is a list of triplets ("pattern", "image url", "thumbnail url")
    that describe how to create image and thumbnail url from a the
    linked_content_url that matches the regular expression "pattern".

    "image url" can be callable to allow for api calls necessary, e.g.,
    for Vimeo or Soundcloud content pieces.
'''

patterns = (
    (re.compile('^.*\\.(jpeg|jpg|png|tiff|tif)$'),  # Images
     '%(url)s',                                     # Represent themselves
     '%(url)s'),                                    # also as thumbnails
    # YouTube Videos short link
    (re.compile('^https://youtu.be/(?P<vid>[-\\w]+)$'),
     'https://img.youtube.com/vi/%(vid)s/maxresdefault.jpg',
     'https://img.youtube.com/vi/%(vid)s/hqdefault.jpg'),
    # YouTube Videos long link
    (re.compile('^https://www.youtube.com/watch\\?v=(?P<vid>[-\\w]+)$'),
     'https://img.youtube.com/vi/%(vid)s/maxresdefault.jpg',
     'https://img.youtube.com/vi/%(vid)s/hqdefault.jpg'),
    # Vimeo Videos (requires api)
    (re.compile('^https://vimeo.com/(?P<id>[0-9]+)$'),
     vimeo_api, None),
    # Soundcloud tracks (requires api)
    (re.compile('^https://soundcloud.com/'
                '(?P<name>[-\\w]+)/(?P<track>[-\\w]+)$'),
     soundcloud_api, None),
)


class LinkedContent (object):
    '''
        Mixin for the post model to create image and thumbnail urls for
        linked content.
    '''
    def get_linked_content_images(self, url):
        for p, img, thumb in patterns:
            match = p.match(url)
            if match:
                parameters = match.groupdict()
                parameters['url'] = url
                if callable(img):
                    return img(**parameters)
                else:
                    return (img % parameters, thumb % parameters)
        return None
