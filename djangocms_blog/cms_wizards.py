# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

try:
    from cms.wizards.wizard_base import Wizard
    from cms.wizards.wizard_pool import wizard_pool
    from django import forms
    from django.utils.text import slugify
    from django.utils.translation import ugettext_lazy as _
    from parler.forms import TranslatableModelForm

    from .cms_appconfig import BlogConfig
    from .models import Post


    class PostWizardForm(TranslatableModelForm):

        default_appconfig = None

        def __init__(self, *args, **kwargs):
            kwargs['initial']['app_config'] = self.default_appconfig
            if 'data' in kwargs:
                kwargs['data']['1-app_config'] = self.default_appconfig
            super(PostWizardForm, self).__init__(*args, **kwargs)
            self.fields['app_config'].widget.attrs['disabled'] = True

        class Meta:
            model = Post
            fields = ['app_config', 'title', 'abstract', 'categories']


    class PostWizard(Wizard):
        template_name = 'djangocms_blog/wizards/create.html'


    for config in BlogConfig.objects.all().order_by('namespace'):
        new_wizard = type(slugify(config.app_title), (PostWizard,), {})
        new_form = type('{0}Form'.format(slugify(config.app_title)), (PostWizardForm,), {
            'default_appconfig': config.pk
        })
        post_wizard = new_wizard(
            title=_('New {0}').format(config.object_name),
            weight=200,
            form=new_form,
            description=_('Create a new {0} in {1}').format(config.object_name, config.app_title),
        )
        wizard_pool.register(post_wizard)
except ImportError:
    # For django CMS version not supporting wizards just ignore this file
    pass
