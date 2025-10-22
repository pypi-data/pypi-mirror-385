from typing import Dict

from NEMO.models import Project, Tool, User
from NEMO.serializers import ModelSerializer
from NEMO.templatetags.custom_tags_and_filters import app_installed
from NEMO.views.constants import CHAR_FIELD_MAXIMUM_LENGTH, CHAR_FIELD_MEDIUM_LENGTH
from rest_flex_fields.serializers import FlexFieldsSerializerMixin
from rest_framework import serializers
from rest_framework.fields import CharField, IntegerField, ListField

from NEMO_publications.models import (
    PublicationData,
    PublicationDataM2MValidationError,
    PublicationMetadata,
    UserPublicationStatus,
    validation_publication_data_m2m,
)
from NEMO_publications.utils import sanitize_doi


class PublicationMetadataSerializer(FlexFieldsSerializerMixin, ModelSerializer):
    class Meta:
        model = PublicationMetadata
        fields = "__all__"
        expandable_fields = {
            "creator": "NEMO.serializers.UserSerializer",
        }


class PublicationDataSerializer(FlexFieldsSerializerMixin, ModelSerializer):
    class Meta:
        model = PublicationData

        fields = "__all__"
        expandable_fields = {
            "metadata": "NEMO_publications.serializers.PublicationMetadataSerializer",
            "tools": ("NEMO.serializers.ToolSerializer", {"many": True}),
            "authors": ("NEMO.serializers.UserSerializer", {"many": True}),
            "projects": ("NEMO.serializers.ProjectSerializer", {"many": True}),
            "creator": "NEMO.serializers.UserSerializer",
        }

    def validate(self, data):
        try:
            m2m_fields = {
                "authors": User.objects.filter(id__in=[obj.id for obj in data["authors"]] if data["authors"] else []),
                "projects": Project.objects.filter(
                    id__in=[obj.id for obj in data["projects"]] if data["projects"] else []
                ),
                "tools": Tool.objects.filter(id__in=[obj.id for obj in data["tools"]] if data["tools"] else []),
            }
            validation_publication_data_m2m(m2m_fields, data["creator"])
            return data
        except PublicationDataM2MValidationError as e:
            raise serializers.ValidationError(e.message)


class PublicationSerializer(serializers.Serializer):
    doi = CharField(max_length=CHAR_FIELD_MAXIMUM_LENGTH, read_only=True)
    title = CharField(max_length=CHAR_FIELD_MAXIMUM_LENGTH, read_only=True)
    journal = CharField(max_length=CHAR_FIELD_MAXIMUM_LENGTH, read_only=True)
    year = IntegerField(read_only=True)
    status = IntegerField(read_only=True)
    authors = ListField()
    tools = ListField()
    projects = ListField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    class Meta:
        fields = "__all__"


# 2025-05-30 Remove when everyone is on NEMO-User-Details >= 1.11.1
USER_DETAILS_PLUGIN_FIELDS = ["employee_id", "orcid", "scopus_id", "researcher_id", "google_scholar_id"]


# This serializer allows sending either a username or a user id
# It now also checks for user details fields and attempts to find a user based on them if no user is present in the request data
class UserPublicationStatusSerializer(serializers.ModelSerializer):
    user = CharField(max_length=CHAR_FIELD_MEDIUM_LENGTH)

    def __init__(self, *args, **kwargs):
        if app_installed("NEMO_user_details"):
            from NEMO_user_details.admin import UserDetailsAdminForm

            # Create new dynamic CharFields for each of the relevant User Details fields.
            details_form = UserDetailsAdminForm()
            try:
                plugin_unique_field_names = details_form._meta.model.unique_identifier_field_names()
            except:
                plugin_unique_field_names = USER_DETAILS_PLUGIN_FIELDS
            for detail_field_name in plugin_unique_field_names:
                setattr(self, f"{detail_field_name}_details_field", details_form.fields.get(detail_field_name))
                if self.user_details_plugin_field(detail_field_name):
                    self.fields[detail_field_name] = CharField(
                        max_length=CHAR_FIELD_MEDIUM_LENGTH, required=False, write_only=True
                    )
        super().__init__(*args, **kwargs)

    class Meta:
        model = UserPublicationStatus
        fields = "__all__"

    def user_details_plugin_field(self, field_name):
        field = getattr(self, f"{field_name}_details_field", None)
        if field and not field.disabled:
            return field
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            representation["user"] = instance.user.id
        except (ValueError, TypeError):
            representation["user"] = None
        return representation

    def validate_user(self, value):
        # Check if the input is a username or ID and fetch the user
        try:
            # Try to process as an ID
            if value.isdigit():
                return User.objects.get(id=value)
            else:
                # Otherwise assume it is a username
                return User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found. Provide a valid username or ID.")

    def to_internal_value(self, data):
        request_data = data.copy()
        if not request_data.get("user") and app_installed("NEMO_user_details"):
            user_details_field_values: Dict[str, str] = {}
            for detail_field_name in USER_DETAILS_PLUGIN_FIELDS:
                user_detail_field = self.user_details_plugin_field(detail_field_name)
                # get the value, but then remove it with pop so it doesn't get passed to UserPublicationStatus() (later) to create it'
                user_detail_field_value = request_data.get(detail_field_name, None)
                request_data.pop(detail_field_name, None)
                if user_detail_field and user_detail_field_value:
                    user_details_field_values[detail_field_name] = user_detail_field_value
            if user_details_field_values:
                # Attempt to find an existing user based on user details fields, if no user value is present
                user, field_name, value = get_user_by_detail_field(user_details_field_values)
                if user:
                    request_data["user"] = user.id
                else:
                    raise serializers.ValidationError(
                        {
                            field_name: [
                                f"Could not find a user with {self.user_details_plugin_field(field_name).label}: {value}."
                            ]
                        }
                    )

        return super().to_internal_value(request_data)

    def validate_doi(self, value):
        return sanitize_doi(value)


def get_user_by_detail_field(user_details_field_values: Dict[str, str]):
    field = None
    value = None

    from NEMO_user_details.models import UserDetails

    for field, value in user_details_field_values.items():
        try:
            return UserDetails.objects.get(**{field: field}).user, field, value
        except UserDetails.DoesNotExist:
            pass
    return None, field, value
