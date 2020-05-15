from channels.generic.websocket import JsonWebsocketConsumer

from ..models import Post


class LiveblogConsumer(JsonWebsocketConsumer):
    def _get_post(self, kwargs):
        apphook = kwargs.get("apphook")
        lang = kwargs.get("lang")
        slug = kwargs.get("post")
        try:
            return Post.objects.namespace(apphook).language(lang).active_translations(slug=slug).get()
        except Post.DoesNotExist:
            return

    def websocket_connect(self, message):
        self.groups = self.get_groups()
        return super().websocket_connect(message)

    def get_groups(self):
        """
        Connect users to the group of the post according to the URL parameters
        """
        post = self._get_post(self.scope["url_route"]["kwargs"])
        if post:
            return [post.liveblog_group]
        else:
            return []
