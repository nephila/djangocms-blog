from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    class Meta:
        app_label = "tests"
