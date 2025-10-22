from __future__ import annotations

from typing import List

from NEMO.models import User
from NEMO.utilities import export_format_datetime
from NEMO.views.api import ModelViewSet, datetime_filters, key_filters, manykey_filters, number_filters, string_filters
from django import forms
from django.db import transaction
from django.forms.models import model_to_dict
from django.http import QueryDict
from drf_excel.mixins import XLSXFileMixin
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from NEMO_publications.forms import create_publication_metadata_post_form
from NEMO_publications.models import PublicationData, PublicationMetadata, UserPublicationStatus
from NEMO_publications.serializers import (
    PublicationDataSerializer,
    PublicationMetadataSerializer,
    PublicationSerializer,
    UserPublicationStatusSerializer,
)
from NEMO_publications.utils import fetch_publication_metadata_by_doi


class PublicationMetadataViewSet(ModelViewSet):
    filename = "publication_metadata"
    queryset = PublicationMetadata.objects.all()
    serializer_class = PublicationMetadataSerializer
    filterset_fields = {
        "id": key_filters,
        "creator": key_filters,
        "creation_time": datetime_filters,
        "doi": string_filters,
        "title": string_filters,
        "journal": string_filters,
        "year": number_filters,
        "month": number_filters,
        "status": number_filters,
        "decision_time": datetime_filters,
    }

    def create(self, request, *args, **kwargs):
        request_user = request.user
        serializer = self.get_serializer(data=request.data)
        datas = serializer.initial_data if getattr(serializer, "many", False) else [serializer.initial_data]
        created = [model_to_dict(self.create_publication_metadata(request_user, data)) for data in datas]
        headers = self.get_success_headers(serializer.initial_data)
        return Response(created, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "Operation not supported."}, status=status.HTTP_404_NOT_FOUND)

    def create_publication_metadata(self, request_user: User, request_data: QueryDict):
        doi = request_data.get("doi")
        if not doi:
            raise ValidationError("DOI is required")
        if not PublicationMetadata.objects.filter(doi__iexact=doi).exists():
            # If metadata for DOI does not exist in DB, lookup in https://doi.org
            publication_metadata_search = fetch_publication_metadata_by_doi(doi)
            # Use user supplied data and override fields with results from DOI search
            metadata_data = request_data.copy()
            metadata_data.update(publication_metadata_search["metadata"])
            publication_metadata_form = create_publication_metadata_post_form(
                metadata_data, request_user, PublicationMetadata()
            )
            publication_metadata_form.instance.creator = request_user
            # If the form is not valid, display any previous errors
            if not publication_metadata_form.is_valid():
                if "error" in publication_metadata_search.keys():
                    publication_metadata_form.add_error(None, [publication_metadata_search["error"]])
                raise ValidationError(publication_metadata_form.errors)
            else:
                return publication_metadata_form.save()
        else:
            raise ValidationError({"error": ["Metadata already exists."]})


class PublicationDataViewSet(ModelViewSet):
    filename = "publication_data"
    queryset = PublicationData.objects.all()
    serializer_class = PublicationDataSerializer
    filterset_fields = {
        "id": key_filters,
        "creator": key_filters,
        "creation_time": datetime_filters,
        "metadata": key_filters,
        "authors": manykey_filters,
        "tools": manykey_filters,
        "projects": manykey_filters,
    }


class PublicationViewSet(XLSXFileMixin, viewsets.GenericViewSet):
    serializer_class = PublicationSerializer

    def check_permissions(self, request):
        if not request or not request.user or not request.user.is_active:
            self.permission_denied(request)

    def list(self, request, *args, **kwargs):
        publication_form = PublicationFilterForm(self.request.GET)
        if not publication_form.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=publication_form.errors)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        publication_form = PublicationFilterForm(self.request.GET)
        publication_form.full_clean()
        data: List[Publication] = []

        publication_metadata_queryset = PublicationMetadata.objects.all()

        if publication_form.get_status():
            publication_metadata_queryset = publication_metadata_queryset.filter(status=publication_form.get_status())
        if publication_form.get_year():
            publication_metadata_queryset = publication_metadata_queryset.filter(year=publication_form.get_year())
        if publication_form.get_journal():
            publication_metadata_queryset = publication_metadata_queryset.filter(
                journal__iexact=publication_form.get_journal()
            )
        if publication_form.get_title():
            publication_metadata_queryset = publication_metadata_queryset.filter(
                title__iexact=publication_form.get_title()
            )
        if publication_form.get_doi():
            publication_metadata_queryset = publication_metadata_queryset.filter(doi__iexact=publication_form.get_doi())

        for publication in publication_metadata_queryset.all():
            publication_data_queryset = PublicationData.objects.filter(metadata=publication)
            if publication_form.get_tool_id():
                publication_data_queryset = publication_data_queryset.filter(tools__id=publication_form.get_tool_id())
            if publication_form.get_author_id():
                publication_data_queryset = publication_data_queryset.filter(
                    authors__id=publication_form.get_author_id()
                )
            if publication_form.get_project_id():
                publication_data_queryset = publication_data_queryset.filter(
                    projects__id=publication_form.get_project_id()
                )

            if publication_data_queryset.exists():
                data.append(Publication(publication, PublicationData.objects.filter(metadata=publication).all()))

        return data

    def get_filename(self, *args, **kwargs):
        return f"publications-{export_format_datetime()}.xlsx"


class Publication(object):
    def __init__(self, metadata: PublicationMetadata, entries: List[PublicationData]):
        self.doi = metadata.doi
        self.title = metadata.title
        self.journal = metadata.journal
        self.year = metadata.year
        self.status = metadata.status
        self.authors = set()
        self.projects = set()
        self.tools = set()
        for entry in entries:
            self.authors.update(entry.authors.all().values_list("id", flat=True))
            self.projects.update(entry.projects.all().values_list("id", flat=True))
            self.tools.update(entry.tools.all().values_list("id", flat=True))


class PublicationFilterForm(forms.Form):
    doi = forms.CharField(required=False)
    journal = forms.CharField(required=False)
    year = forms.CharField(required=False)
    title = forms.CharField(required=False)
    status = forms.IntegerField(required=False)
    author_id = forms.IntegerField(required=False)
    tool_id = forms.IntegerField(required=False)
    project_id = forms.IntegerField(required=False)

    def get_doi(self):
        return self.cleaned_data["doi"]

    def get_journal(self):
        return self.cleaned_data["journal"]

    def get_year(self):
        return self.cleaned_data["year"]

    def get_title(self):
        return self.cleaned_data["title"]

    def get_author_id(self):
        return self.cleaned_data["author_id"]

    def get_tool_id(self):
        return self.cleaned_data["tool_id"]

    def get_project_id(self):
        return self.cleaned_data["project_id"]

    def get_status(self):
        return self.cleaned_data["status"]


class UserPublicationStatusViewSet(ModelViewSet):
    filename = "user_publication_status"
    queryset = UserPublicationStatus.objects.all()
    serializer_class = UserPublicationStatusSerializer
    filterset_fields = {
        "id": key_filters,
        "user": key_filters,
        "doi": string_filters,
        "date_added": datetime_filters,
        "status": number_filters,
    }

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # We are overriding this to remove rows that would trigger the UniqueConstraint
        # Essentially, this allows uploading a list with duplicates, and it won't throw an error
        many = isinstance(request.data, list)
        if not many:
            return super().create(request, *args, **kwargs)
        else:
            serializer = self.get_serializer(data=request.data, many=many)
            safe_data = [data for data in request.data if not is_unique_constraint_error(serializer, data)]
            serializer = self.get_serializer(data=safe_data, many=many)
            serializer.is_valid(raise_exception=True)
            try:
                self.perform_create(serializer)
            except Exception as e:
                raise ValidationError({"error": str(e)})
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, headers=headers)


def is_unique_constraint_error(serializer, data):
    try:
        serializer.run_child_validation(data)
        return False  # If no exception, the data is valid
    except ValidationError as exc:
        str_e = str(exc)
        return "user" in str_e and "doi" in str_e and "unique" in str_e
