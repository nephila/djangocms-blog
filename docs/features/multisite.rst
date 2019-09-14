

.. _multisite:

#########
Multisite
#########

django CMS blog provides full support for multisite setups.

***************
Basic multisite
***************

To enabled basic multisite add ``BLOG_MULTISITE = True`` to the project settings.

Each blog post can be assigned to none, one or more sites: if no site is selected, then
it's visible on all sites. All users with permission on the blog can manage all the blog
posts, whichever the sites are.

*********************
Multisite permissions
*********************

Multisite permissions allow to restrict users to only manage the blog posts for the
sites they are enabled to

To implement the multisite permissions API, you must add a ``get_sites`` method on
the user model which returns a queryset of sites the user is allowed to add posts to.

Example:

.. code-block:: python

    class CustomUser(AbstractUser):
        sites = models.ManyToManyField('sites.Site')

        def get_sites(self):
            return self.sites
