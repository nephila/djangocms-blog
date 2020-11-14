from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import Vimeo, YoutTubeVideo


@plugin_pool.register_plugin
class YouTubePlugin(CMSPluginBase):
    model = YoutTubeVideo
    module = "Media"
    name = "You Tube"
    render_template = "media_app/youtube.html"


@plugin_pool.register_plugin
class VimeoPlugin(CMSPluginBase):
    model = Vimeo
    module = "Media"
    name = "Vimeo"
    render_template = "media_app/vimeo.html"
