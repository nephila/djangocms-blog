
.. _cms-wizard:

######################
django CMS 3.2+ Wizard
######################

django CMS 3.2+ provides a content creation wizard that allows to quickly created supported
content types, such as blog posts.

For each configured Apphook, a content type is added to the wizard.

Some issues with multiple registrations raising django CMS ``AlreadyRegisteredException``
hae been reported; to handle these cases gracefully, the exception is swallowed
when Django ``DEBUG == True`` avoiding breaking production websites. In these cases they
wizard may not show up, but the rest will work as intended.

Wizard can create blog post content by filling the ``Text`` form field. You can control the text plugin used for
content creation by editing two settings:

* ``BLOG_WIZARD_CONTENT_PLUGIN``: name of the plugin to use (default: ``TextPlugin``)
* ``BLOG_WIZARD_CONTENT_PLUGIN_BODY``: name of the plugin field to add text to (default: ``body``)

.. warning:: the plugin used must only have the text field required, all additional fields must be optional, otherwise
             the wizard will fail.
