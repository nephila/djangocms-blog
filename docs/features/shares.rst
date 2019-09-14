.. _shares:

#############
Social shares
#############

``djangocms_blog`` integrates well with options for social shares. One of the many options available is Shariff_ which was developed by a popular German computer magazine.

.. _Shariff: https://github.com/heiseonline/shariff

To allow readers to share articles on Facebook, Twitter, LinkedIn or just email, add the share buttons to your ``post_detail.html`` template just before ``</article>``.

If you decide to use Shariff this requires a ``<div>`` to be added (see documentation of shariff).

See below for a template tag that loads all required configurations and javascript files. The ``<div>`` is then replaced by ``{% shariff %}``:

.. code-block:: python

    from django.conf import settings
    from django import template

    register = template.Library()

    @register.inclusion_tag('djangocms_blog/shariff.html', takes_context=True)
    def shariff(context, title=None, services=None, orientation=None):
        context['orientation'] = orientation if orientation else 'horizontal'
        context['services'] = escape(services if services else
                                    settings.SHARIFF['services'])  # MUST be configured in settings.py
        if title:
            context['short_message'] = settings.SHARIFF.get('prefix', '') + title +\
                          settings.SHARIFF.get('postfix', '')
        if 'mail-url' in settings.SHARIFF:
            context['mail_url'] = settings.SHARIFF['mail-url']
        return(context)

And in ``templates/djangocms_blog/shariff.html`` you need:

.. code-block:: html+django

    {% load static sekizai_tags %}
    {% addtoblock 'js' %}<script src="{% static 'js/shariff.min.js' %}"></script>{% endaddtoblock %}
    {% addtoblock 'css' %}<link href="{% static 'css/shariff.min.css' %}" rel="stylesheet">{% endaddtoblock %}
    <div class="shariff" data-services="{{services}}" data-orientation="{{orientation}}"{% if mail_url %} data-mail-url="{{mail_url}}"{% endif %}{% if short_message %} data-title="{{short_message}}"{% endif %}></div>

The shariff files ``js/shariff.min.js`` and ``css/shariff.min.css`` will need to be added to your static files. Also, a little configuration in ``settings.py`` is needed, e.g.,

.. code-block:: python

    SHARIFF = {
        'services': '["twitter", "facebook", "googleplus", "linkedin", "xing", "mail"]',
        'mail-url': 'mailto:',                  # optional
        'prefix':   'Have you seen this: "',	# optional
        'postfix':  '"',                        # optional
    }
