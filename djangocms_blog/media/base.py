# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals


class MediaAttachmentPluginMixin(object):
    _media_autoconfiguration = {
        'params': [],
        'thumb_url': '',
        'main_url': '',
        'thumb_callable': None,
        'main_callable': None,
    }
    _cached_params = None

    @property
    def _media_params(self):
        if not self._cached_params:
            for pattern in self._media_autoconfiguration['params']:
                match = pattern.match(self._media_url)
                if match:
                    if self._media_autoconfiguration['callable']:
                        self._cached_params = getattr(
                            self, self._media_autoconfiguration['callable']
                        )(**match.groupdict())
                    else:
                        self._cached_params = match.groupdict()
                        self._cached_params['url'] = self._media_url
        return self._cached_params

    @property
    def _media_url(self):
        raise NotImplementedError

    def get_main_image(self):
        return self._media_autoconfiguration['main_url'] % self._media_params

    def get_thumb_image(self):
        return self._media_autoconfiguration['thumb_url'] % self._media_params
