
.. _blog-content-hub:

###########################
Organizing content in a hub
###########################

A content hub is a centralized online destination that contains curated content
around a specific topic. There are potentially significant SEO benefits to creating
a content hub.

While a traditional blog shows posts ordered by time of publication, posts in a content
hub are organized around categories and their priority is curated by the editors. Content
is updated more often and does not get hidden by pagination.

``djangocms-blog`` implements content hubs through categories. ``djangocms-blog`` categories have a
hierarchical structure which is the basis for a content hub representation. Each category is
complemented by optional additional properties:

- a description (HTML field),

- priority (to give the categories an order) and

- a category image (just like post images)

Using the `Organizing content in a hub`_ you can decide on a per apphook base if you would like a traditional
blog representation of the blog's content or the content hub representation.

The ``Post`` model has an attribute ``pinned``:

.. py:attribute:: Post.pinned

    ``pinned`` is an integer or empty and is used to affect the order in which blog posts are presented.
    They are sorted in ascending order of the value ``pinned`` (empty values last) and the in descending
    order by date.

The ``BlogCategory`` model has four attributes that allow to traverse the category structure:

.. py:attribute:: BlogCategory.priority

    Blog categories are sorted in ascending order of their ``priority`` value.

.. py:attribute:: BlogCategory.linked_posts

   Gives all posts of the current namespace (i.e. apphook) that are linked to a category

.. py:attribute:: BlogCategory.pinned_posts

    Gives all posts of the current namespace (i.e. apphook) that are linked to a category and have
    positive ``pinned`` value. By convention curated posts for content hub are marked by pinning them.
    Posts are returned in ascending order of their ``pinned`` attribute. Hence the numbers can be used to
    give posts a desired order.

.. py:attribute:: BlogCategory.children

    This returns an iterable of all child categories of a given category.


