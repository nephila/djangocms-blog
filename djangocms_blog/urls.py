from .urls_base import get_urls


# module-level app_name attribute as per django 1.9+
app_name = "djangocms_blog"
urlpatterns = get_urls(
    post_list_path="",
    category_path="category/"
)
