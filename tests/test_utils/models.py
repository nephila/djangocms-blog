# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    sites = models.ManyToManyField('sites.Site')

    def get_sites(self):
        return self.sites
