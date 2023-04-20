import django.contrib.auth.models
import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "__first__"),
        ("sites", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                ("id", models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name="ID")),
                ("password", models.CharField(verbose_name="password", max_length=128)),
                ("last_login", models.DateTimeField(verbose_name="last login", null=True, blank=True)),
                (
                    "is_superuser",
                    models.BooleanField(
                        verbose_name="superuser status",
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        default=False,
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        help_text="Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        unique=True,
                        verbose_name="username",
                        validators=[
                            django.core.validators.RegexValidator(
                                "^[\\w.@+-]+$",
                                "Enter a valid username. This value may contain only letters, "
                                "numbers and @/./+/-/_ characters.",
                                "invalid",
                            )
                        ],
                        max_length=30,
                        error_messages={"unique": "A user with that username already exists."},
                    ),
                ),
                ("first_name", models.CharField(verbose_name="first name", max_length=30, blank=True)),
                ("last_name", models.CharField(verbose_name="last name", max_length=30, blank=True)),
                ("email", models.EmailField(verbose_name="email address", max_length=254, blank=True)),
                (
                    "is_staff",
                    models.BooleanField(
                        verbose_name="staff status",
                        help_text="Designates whether the user can log into this admin site.",
                        default=False,
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        verbose_name="active",
                        help_text="Designates whether this user should be treated as active. "
                        "Unselect this instead of deleting accounts.",
                        default=True,
                    ),
                ),
                ("date_joined", models.DateTimeField(verbose_name="date joined", default=django.utils.timezone.now)),
                (
                    "groups",
                    models.ManyToManyField(
                        help_text="The groups this user belongs to. A user will get all "
                        "permissions granted to each of their groups.",
                        related_query_name="user",
                        related_name="user_set",
                        verbose_name="groups",
                        blank=True,
                        to="auth.Group",
                    ),
                ),
                ("sites", models.ManyToManyField(to="sites.Site")),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        help_text="Specific permissions for this user.",
                        related_query_name="user",
                        related_name="user_set",
                        verbose_name="user permissions",
                        blank=True,
                        to="auth.Permission",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "abstract": False,
                "verbose_name_plural": "users",
            },
            bases=(models.Model,),
        ),
    ]
