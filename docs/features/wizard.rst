
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
