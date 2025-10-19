from django.apps import AppConfig
from django.conf import settings

class DjangoFullnameLocalizationConfig(AppConfig):
    name = 'django_fullname_localization'

    def ready(self):
        from django.contrib.auth.models import AbstractUser
        
        def get_full_name(self):
            """
            Add localization support for user's fullname.
            """
            full_name_template = getattr(settings, "FULL_NAME_TEMPLATE", "{user.last_name}{user.first_name}")
            full_name = full_name_template.format(user=self)
            return full_name
        
        AbstractUser.get_full_name = get_full_name

        if getattr(settings, "USE_FULL_NAME_INSTEAD_OF_SHORT_NAME", True):
            AbstractUser.get_short_name = get_full_name
