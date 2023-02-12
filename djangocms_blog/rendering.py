from django.template.response import TemplateResponse


def render_post_content(request, content_object):
    template = 'djangocms_blog/post_detail.html'
    context = {
        'post': content_object,   # Temporary to allow for easier transition from v3 to v4
        'post_content': content_object,
    }
    return TemplateResponse(request, template, context)
