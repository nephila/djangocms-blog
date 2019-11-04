# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    sites = models.ManyToManyField('sites.Site')

    def get_sites(self):
        return self.sites
