from NEMO.decorators import customization
from NEMO.views.customization import CustomizationBase


@customization(key="publications", title="Publications")
class PublicationsCustomization(CustomizationBase):
    variables = {
        "publications_enable_landing_carousel": "",
        "publications_carousel_latest_display_count": "10",
        "publications_carousel_latest_display_order": '["-creation_time"]',
        "publications_carousel_tiles_per_item": "2",
        "publications_carousel_interval_time": "5",
        "publications_carousel_show_date": "enabled",
        "publications_carousel_show_authors": "enabled",
        "publications_carousel_show_projects": "enabled",
        "publications_carousel_show_tools": "enabled",
        "publications_notification_expiration_days": "365",
        "publications_enable_landing_warning_pending_publications": "",
    }
