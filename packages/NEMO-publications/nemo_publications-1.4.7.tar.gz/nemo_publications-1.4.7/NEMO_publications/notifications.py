from __future__ import annotations
from datetime import timedelta
from typing import TYPE_CHECKING

from NEMO.models import Notification
from NEMO.views.notifications import delete_notification
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from NEMO_publications.customization import PublicationsCustomization
from NEMO_publications.utils import PUBLICATION_NOTIFICATION

if TYPE_CHECKING:
    from NEMO_publications.models import UserPublicationStatus


def manage_publication_notification(user_publication_status: UserPublicationStatus):
    from NEMO_publications.models import UserPublicationStatus

    if user_publication_status.status == UserPublicationStatus.Status.PENDING:
        expiration = timezone.now() + timedelta(
            days=PublicationsCustomization.get_int("publications_notification_expiration_days")
        )  # days for publication notifications to expire
        Notification.objects.get_or_create(
            user=user_publication_status.user,
            notification_type=PUBLICATION_NOTIFICATION,
            content_type=ContentType.objects.get_for_model(user_publication_status),
            object_id=user_publication_status.id,
            defaults={"expiration": expiration},
        )
    else:
        delete_publication_notification(user_publication_status)


def delete_publication_notification(user_publication_status: UserPublicationStatus):
    delete_notification(PUBLICATION_NOTIFICATION, user_publication_status.id, [user_publication_status.user])
