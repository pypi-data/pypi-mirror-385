from django.apps import AppConfig
from django.conf import settings

from . import app_settings as defaults

# Set some app default settings
for name in dir(defaults):
    if name.isupper() and not hasattr(settings, name):
        setattr(settings, name, getattr(defaults, name))


class NemoPublicationsConfig(AppConfig):
    name = "NEMO_publications"
    verbose_name = "NEMO Publications"

    def ready(self):
        from django.utils.translation import gettext_lazy as _
        from NEMO.plugins.utils import (
            add_dynamic_notification_types,
            check_extra_dependencies,
        )
        from NEMO_publications.utils import PUBLICATION_NOTIFICATION

        check_extra_dependencies(self.name, ["NEMO", "NEMO-CE"])

        add_dynamic_notification_types(
            [(PUBLICATION_NOTIFICATION, _("Publications - notifies of suggested publications for users"))]
        )
