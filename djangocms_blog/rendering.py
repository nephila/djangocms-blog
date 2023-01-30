from django.template.response import TemplateResponse


def render_post_content(request, content_object):
    template = 'djangocms_blog/post_detail.html'
    context = {'post': content_object}
    return TemplateResponse(request, template, context)
