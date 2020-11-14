import warnings

from cms.api import add_plugin
from cms.utils.permissions import get_current_user
from cms.wizards.wizard_base import Wizard
from cms.wizards.wizard_pool import AlreadyRegisteredException, wizard_pool
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .cms_appconfig import BlogConfig
from .fields import slugify
from .forms import PostAdminFormBase
from .models import Post
from .settings import get_setting


class PostWizardForm(PostAdminFormBase):
    default_appconfig = None

    slug = forms.SlugField(
        label=_("Slug"),
        max_length=752,
        required=False,
        help_text=_("Leave empty for automatic slug, or override as required."),
    )

    def __init__(self, *args, **kwargs):
        if "initial" not in kwargs or not kwargs.get("initial", False):
            kwargs["initial"] = {}
        kwargs["initial"]["app_config"] = self.default_appconfig
        if "data" in kwargs and kwargs["data"] is not None:
            data = kwargs["data"].copy()
            data["1-app_config"] = self.default_appconfig
            kwargs["data"] = data
        super().__init__(*args, **kwargs)
        self.fields["app_config"].widget = forms.Select(
            attrs=self.fields["app_config"].widget.attrs,
            choices=self.fields["app_config"].widget.choices,
        )
        self.fields["app_config"].widget.attrs["disabled"] = True
        if "categories" in self.fields:
            self.fields["categories"].queryset = self.available_categories

    class Meta:
        model = Post
        fields = ["app_config", "title", "slug", "abstract", "categories"]

    class Media:
        js = (
            "admin/js/vendor/jquery/jquery.js",
            "admin/js/jquery.init.js",
        )

    def save(self, commit=True):
        self.instance._set_default_author(get_current_user())
        instance = super().save(commit)
        self.add_plugin()
        return instance

    def clean_slug(self):
        """
        Generate a valid slug, in case the given one is taken
        """
        source = self.cleaned_data.get("slug", "")
        lang_choice = self.language_code
        if not source:
            source = slugify(self.cleaned_data.get("title", ""))
        qs = Post._default_manager.active_translations(lang_choice).language(lang_choice)
        used = list(qs.values_list("translations__slug", flat=True))
        slug = source
        i = 1
        while slug in used:
            slug = "{}-{}".format(source, i)
            i += 1
        return slug

    def add_plugin(self):
        """
        Add text field content as text plugin to the blog post.
        """
        text = self.cleaned_data.get("post_text", "")
        app_config = self.cleaned_data.get("app_config", None)
        plugin_type = get_setting("WIZARD_CONTENT_PLUGIN")
        plugin_body = get_setting("WIZARD_CONTENT_PLUGIN_BODY")
        if text and app_config.use_placeholder:
            opts = {
                "placeholder": self.instance.content,
                "plugin_type": plugin_type,
                "language": self.language_code,
                plugin_body: text,
            }
            add_plugin(**opts)


class PostWizard(Wizard):
    pass


for config in BlogConfig.objects.all().order_by("namespace"):
    seed = slugify("{}.{}".format(config.app_title, config.namespace))
    new_wizard = type(str(seed), (PostWizard,), {})
    new_form = type("{}Form".format(seed), (PostWizardForm,), {"default_appconfig": config.pk})
    post_wizard = new_wizard(
        title=_("New {0}").format(config.object_name),
        weight=200,
        form=new_form,
        model=Post,
        description=_("Create a new {0} in {1}").format(config.object_name, config.app_title),
    )
    try:
        wizard_pool.register(post_wizard)
    except AlreadyRegisteredException:  # pragma: no cover
        if settings.DEBUG:
            raise
        else:
            warnings.warn(
                "Wizard {} cannot be registered. Please make sure that "
                "BlogConfig.namespace {} and BlogConfig.app_title {} are"
                "unique together".format(seed, config.namespace, config.app_title)
            )
