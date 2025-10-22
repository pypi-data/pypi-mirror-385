from django.core.exceptions import ValidationError
from django.forms import ModelForm

from NEMO_publications.models import (
    PublicationData,
    PublicationDataM2MValidationError,
    PublicationMetadata,
    UserPublicationStatus,
    validation_publication_data_m2m,
)
from NEMO_publications.utils import sanitize_doi


class PublicationDataForm(ModelForm):
    class Meta:
        model = PublicationData
        exclude = ["creation_time", "creator", "metadata"]

    def clean(self):
        cleaned_data = super().clean()
        try:
            validation_publication_data_m2m(cleaned_data, self.instance.creator)
            return cleaned_data
        except PublicationDataM2MValidationError as e:
            raise ValidationError(e.message)


class PublicationMetadataForm(ModelForm):
    class Meta:
        model = PublicationMetadata
        exclude = ["creation_time", "creator"]


class UserPublicationStatusForm(ModelForm):
    class Meta:
        model = UserPublicationStatus
        fields = "__all__"

    def clean_doi(self):
        return sanitize_doi(self.cleaned_data.get("doi"))


def create_publication_metadata_post_form(content, user, publication_metadata):
    return PublicationMetadataForm(
        content,
        instance=publication_metadata,
        initial={"creator": user},
    )


def create_publication_data_post_form(request, user, edit, publication_data):
    return PublicationDataForm(
        request.POST,
        instance=publication_data,
        initial={"creator": publication_data.creator if edit else user},
    )
