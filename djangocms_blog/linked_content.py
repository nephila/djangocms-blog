# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import re

import requests
from django.conf import settings


def add_patterns(cls):
    cls.patterns = (
        # Images
        (re.compile('^.*\\.(jpeg|jpg|png|tiff|tif)$'),
         '%(url)s',                                 # Represent themselves
         '%(url)s'),                                # also as thumbnails
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
         cls.vimeo_api, None),
        # Soundcloud tracks (requires api)
        (re.compile('^https://soundcloud.com/(?P<name>[-\\w]+)/(?P<track>[-\\w]+)$'),
         cls.soundcloud_api, None),

    )
    return cls


@add_patterns
class LinkedContent (object):

    def vimeo_api(id, url):
        json = requests.get('http://vimeo.com/api/v2/video/%s.json' % id).json()
        return (json[0]['thumbnail_large'], json[0]['thumbnail_medium'])

    def soundcloud_api(name, track, url):
        json = requests.get('http://api.soundcloud.com/resolve?client_id='
                            '%(client_id)s&'
                            'url=https://soundcloud.com/%(name)s/%(track)s' %
                            {
                                'client_id': getattr(settings, 'SOUNDCLOUD_APIKEY',
                                                     'LvWovRaJZlWCHql0bISuum8Bd2KX79mb'),
                                'name': name,
                                'track': track,
                             }).json()
        thumbnail = json['waveform_url']
        if 'artwork_url' in json and json['artwork_url']:
            thumbnail = json['artwork_url'].replace('large.jpg', 'crop.jpg')
        return (json['waveform_url'], thumbnail)

    def get_linked_content_images(self, url):
        if not url:
            return None
        for p, img, thumb in self.patterns:
            match = p.match(url)
            if match:
                parameters = match.groupdict()
                parameters['url'] = url
                if callable(img):
                    return img(**parameters)
                else:
                    return (img % parameters, thumb % parameters)
        return None
