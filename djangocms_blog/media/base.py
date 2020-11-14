class MediaAttachmentPluginMixin:
    """
    Base class for media-enabled plugins.

    Items that needs implementation in subclasses:

    * media_id: property that provides the object id on the external platform
    * media_url: property that provides the media public URL
    * _media_autoconfiguration: configuration dictionary (see documentation for details)
    """

    _media_autoconfiguration = {
        "params": [],
        "thumb_url": "",
        "main_url": "",
        "callable": None,
    }
    """
    Configuration dictionary. **All** the keys are required:

    * ``'params'``: one or more regular expressions to retrieve the media ID
      according to the provided ``media_url``. It **must** contain a capturing
      group called ``media_id`` (see examples below).
    * ``'thumb_url'``: URL of the intermediate resolution media cover (depending
      on the plaform).
      It supports string formatting via ``format`` by providing the return json
      for the media according to the plugic specification.
    * ``'main_url'``: URL of the maximum resolution media cover (depending
      on the plaform).
      It supports string formatting via ``%``-formatting by providing the
      return json for the media according to the plugic specification.
    * ``'callable'``: in case the above information are not recoverable from the
      object URL, provide here the name of a method on the plugin model instance
      taking the ``media_id`` as parameter and that builds the data required by
      ``thumb_url``, ``media_url`` strings to build the correct cover urls.

    """
    _cached_params = None

    @property
    def media_params(self):
        """
        Retrieves the media information.

        Minimal keys returned:

        * ``media_id``: object id on the external platform
        * ``url``: full url to the public version of the media

        In case the ``'callable'`` key in py:attr:` _media_autoconfiguration` is not ``None``, it
        will be called instead (as method on the current model instance) to retrieve the
        information with any required logic.

        :return: media information dictionary
        :rtype: dict
        """
        if not self._cached_params:
            for pattern in self._media_autoconfiguration["params"]:
                match = pattern.match(self.media_url)
                if match:
                    if self._media_autoconfiguration["callable"]:
                        self._cached_params = getattr(self, self._media_autoconfiguration["callable"])(
                            **match.groupdict()
                        )
                    else:
                        self._cached_params = match.groupdict()
                        self._cached_params["url"] = self.media_url
        return self._cached_params

    @property
    def media_url(self):
        """
        Public URL of the object on the remote media.

        As you will likely have a ``URL`` on the plugin model,
        it's usually enough to return that value, but you are free to implement
        any way to retrieve it.

        :rtype: str
        """
        raise NotImplementedError

    @property
    def media_id(self):
        """
        ID of the object on the remote media.

        :rtype: str
        """
        try:
            return self.media_params["media_id"]
        except KeyError:  # pragma: no cover
            return None

    def get_main_image(self):
        """
        URL of the media cover at maximum resolution

        :rtype: str
        """
        return self._media_autoconfiguration["main_url"] % self.media_params

    def get_thumb_image(self):
        """
        URL of the media cover at intermediate resolution

        :rtype: str
        """
        return self._media_autoconfiguration["thumb_url"] % self.media_params
