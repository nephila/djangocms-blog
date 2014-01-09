# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^djangocms_blog\.fields\.UsersWithPermsManyToManyField"])


class UsersWithPermsManyToManyField(models.ManyToManyField):

    def __init__(self, perms, **kwargs):

        (super(UsersWithPermsManyToManyField, self)
         .__init__(User, limit_choices_to=self.get_limit_choices_to(perms),
                   **kwargs))

    def get_limit_choices_to(self, perms):
        return (models.Q(user_permissions__codename__in=perms)
                | models.Q(groups__permissions__codename__in=perms)
                | models.Q(is_superuser=True))

    def formfield(self, **kwargs):
        db = kwargs.pop('using', None)
        defaults = {
            'queryset': (self.rel.to._default_manager.using(db)
                         .complex_filter(self.rel.limit_choices_to).distinct())
        }
        defaults.update(kwargs)

        return super(UsersWithPermsManyToManyField, self).formfield(**defaults)