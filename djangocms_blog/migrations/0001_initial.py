import cms.models.fields
import django.utils.timezone
import djangocms_text_ckeditor.fields
import filer.fields.image
import meta.models
import taggit_autosuggest.managers
from django.conf import settings
from django.db import migrations, models
from filer.settings import FILER_IMAGE_MODEL

from djangocms_blog.models import thumbnail_model

ACTUAL_FILER_IMAGE_MODEL = FILER_IMAGE_MODEL or "filer.Image"


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        migrations.swappable_dependency(ACTUAL_FILER_IMAGE_MODEL),
        ("cms", "__first__"),
        ("taggit", "__first__"),
        ("filer", "0003_thumbnailoption"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuthorEntriesPlugin",
            fields=[
                (
                    "cmsplugin_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="cms.CMSPlugin",
                        on_delete=models.deletion.CASCADE,
                    ),
                ),
                (
                    "latest_posts",
                    models.IntegerField(
                        default=5, help_text="The number of author articles to be displayed.", verbose_name="Articles"
                    ),
                ),
                ("authors", models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name="Authors")),
            ],
            options={
                "abstract": False,
            },
            bases=("cms.cmsplugin",),
        ),
        migrations.CreateModel(
            name="BlogCategory",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("date_created", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("date_modified", models.DateTimeField(auto_now=True, verbose_name="modified at")),
                (
                    "parent",
                    models.ForeignKey(
                        verbose_name="parent",
                        blank=True,
                        to="djangocms_blog.BlogCategory",
                        null=True,
                        on_delete=models.deletion.CASCADE,
                    ),
                ),
            ],
            options={
                "verbose_name": "blog category",
                "verbose_name_plural": "blog categories",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="BlogCategoryTranslation",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "language_code",
                    models.CharField(
                        db_index=True, max_length=15, verbose_name="Language", choices=settings.LANGUAGES
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="name")),
                ("slug", models.SlugField(verbose_name="slug", blank=True)),
                (
                    "master",
                    models.ForeignKey(
                        related_name="translations",
                        editable=False,
                        to="djangocms_blog.BlogCategory",
                        null=True,
                        on_delete=models.deletion.CASCADE,
                    ),
                ),
            ],
            options={
                "db_table": "djangocms_blog_blogcategory_translation",
                "verbose_name": "blog category Translation",
                "default_permissions": (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="LatestPostsPlugin",
            fields=[
                (
                    "cmsplugin_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="cms.CMSPlugin",
                        on_delete=models.deletion.CASCADE,
                    ),
                ),
                (
                    "latest_posts",
                    models.IntegerField(
                        default=5, help_text="The number of latests articles to be displayed.", verbose_name="Articles"
                    ),
                ),
                (
                    "categories",
                    models.ManyToManyField(
                        help_text="Show only the blog articles tagged with chosen categories.",
                        to="djangocms_blog.BlogCategory",
                        blank=True,
                    ),
                ),
                (
                    "tags",
                    models.ManyToManyField(
                        help_text="Show only the blog articles tagged with chosen tags.", to="taggit.Tag", blank=True
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("cms.cmsplugin",),
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                (
                    "date_published",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="Published Since"),
                ),
                ("date_published_end", models.DateTimeField(null=True, verbose_name="Published Until", blank=True)),
                ("publish", models.BooleanField(default=False, verbose_name="Publish")),
                ("enable_comments", models.BooleanField(default=True, verbose_name="Enable comments on post")),
                (
                    "author",
                    models.ForeignKey(
                        related_name="djangocms_blog_post_author",
                        verbose_name="Author",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.deletion.PROTECT,
                    ),
                ),
                (
                    "categories",
                    models.ManyToManyField(
                        related_name="blog_posts", verbose_name="category", to="djangocms_blog.BlogCategory"
                    ),
                ),
                (
                    "content",
                    cms.models.fields.PlaceholderField(
                        slotname="post_content", editable=False, to="cms.Placeholder", null=True
                    ),
                ),
                (
                    "main_image",
                    filer.fields.image.FilerImageField(
                        related_name="djangocms_blog_post_image",
                        verbose_name="Main image",
                        blank=True,
                        to=ACTUAL_FILER_IMAGE_MODEL,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                    ),
                ),
                (
                    "main_image_full",
                    models.ForeignKey(
                        related_name="djangocms_blog_post_full",
                        verbose_name="Main image full",
                        blank=True,
                        to=thumbnail_model,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                    ),
                ),
                (
                    "main_image_thumbnail",
                    models.ForeignKey(
                        related_name="djangocms_blog_post_thumbnail",
                        verbose_name="Main image thumbnail",
                        blank=True,
                        to=thumbnail_model,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                    ),
                ),
                (
                    "tags",
                    taggit_autosuggest.managers.TaggableManager(
                        to="taggit.Tag",
                        through="taggit.TaggedItem",
                        blank=True,
                        help_text="A comma-separated list of tags.",
                        verbose_name="Tags",
                    ),
                ),
            ],
            options={
                "ordering": ("-date_published", "-date_created"),
                "get_latest_by": "date_published",
                "verbose_name": "blog article",
                "verbose_name_plural": "blog articles",
            },
            bases=(meta.models.ModelMeta, models.Model),
        ),
        migrations.CreateModel(
            name="PostTranslation",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                (
                    "language_code",
                    models.CharField(
                        db_index=True, max_length=15, verbose_name="Language", choices=settings.LANGUAGES
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Title")),
                ("slug", models.SlugField(verbose_name="slug", blank=True)),
                ("abstract", djangocms_text_ckeditor.fields.HTMLField(verbose_name="Abstract")),
                ("meta_description", models.TextField(default="", verbose_name="Post meta description", blank=True)),
                ("meta_keywords", models.TextField(default="", verbose_name="Post meta keywords", blank=True)),
                (
                    "meta_title",
                    models.CharField(
                        default="",
                        help_text="used in title tag and social sharing",
                        max_length=255,
                        verbose_name="Post meta title",
                        blank=True,
                    ),
                ),
                ("post_text", djangocms_text_ckeditor.fields.HTMLField(default="", verbose_name="Text", blank=True)),
                (
                    "master",
                    models.ForeignKey(
                        related_name="translations",
                        editable=False,
                        to="djangocms_blog.Post",
                        null=True,
                        on_delete=models.deletion.CASCADE,
                    ),
                ),
            ],
            options={
                "db_table": "djangocms_blog_post_translation",
                "verbose_name": "blog article Translation",
                "default_permissions": (),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="posttranslation",
            unique_together={("language_code", "master"), ("language_code", "slug")},
        ),
        migrations.AlterUniqueTogether(
            name="blogcategorytranslation",
            unique_together={("language_code", "master"), ("language_code", "slug")},
        ),
    ]
