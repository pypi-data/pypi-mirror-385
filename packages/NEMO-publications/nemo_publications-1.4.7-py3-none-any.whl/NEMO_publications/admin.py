from django.contrib import admin
from django.contrib.admin import register
from django.utils import timezone

from NEMO_publications.forms import PublicationDataForm, UserPublicationStatusForm
from NEMO_publications.models import (
    PublicationData,
    PublicationMetadata,
    PublicationMetadataStatus,
    UserPublicationStatus,
)
from NEMO_publications.utils import fetch_publication_metadata_by_doi
from NEMO_publications.views.publications import export_publications


@admin.action(description="Export selected publications in CSV")
def export_publication_for_metadata(model_admin, request, queryset):
    return export_publications(queryset.all())


@admin.action(description="Reject selected publications")
def reject_publication_metadata(model_admin, request, queryset):
    queryset.all().update(status=PublicationMetadataStatus.REJECTED, decision_time=timezone.now())


@admin.action(description="Approve selected publications")
def approve_publication_metadata(model_admin, request, queryset):
    queryset.all().update(status=PublicationMetadataStatus.APPROVED, decision_time=timezone.now())


@admin.action(description="Delete all associated publication data")
def delete_publication_data(model_admin, request, queryset):
    PublicationData.objects.filter(metadata__in=queryset.all()).delete()


@admin.action(description="Delete all publication metadata without data entries")
def delete_metadata_without_data(model_admin, request, queryset):
    PublicationMetadata.objects.filter(publicationdata=None).delete()


@admin.action(
    description="Fetch metadata for selected publications from remote source using DOI (Replace existing field values with remote values)"
)
def fetch_and_merge_metadata(model_admin, request, queryset):
    for metadata in queryset.all():
        fetch_result = fetch_publication_metadata_by_doi(metadata.doi)
        if "error" not in fetch_result.keys():
            cleaned_fetched_metadata = {k: v for k, v in fetch_result["metadata"].items() if v}
            del cleaned_fetched_metadata["doi"]
            for key, value in cleaned_fetched_metadata.items():
                setattr(metadata, key, value)
            try:
                metadata.save()
            except Exception:
                pass


class StatusFilter(admin.SimpleListFilter):
    title = "Status"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return [
            ("none", "None"),
            *PublicationMetadataStatus.Choices,
        ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        elif self.value() == "none":
            return queryset.filter(status__isnull=True)
        else:
            return queryset.filter(status=self.value())


@register(PublicationMetadata)
class PublicationMetadataAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "journal",
        "month",
        "year",
        "doi",
    )
    list_filter = (
        StatusFilter,
        "year",
        "month",
        ("creator", admin.RelatedOnlyFieldListFilter),
    )
    date_hierarchy = "creation_time"
    actions = [
        export_publication_for_metadata,
        delete_publication_data,
        delete_metadata_without_data,
        reject_publication_metadata,
        approve_publication_metadata,
        fetch_and_merge_metadata,
    ]
    readonly_fields = ["creation_time"]


@register(PublicationData)
class PublicationDataAdmin(admin.ModelAdmin):
    list_display = (
        "creator",
        "creation_time",
        "metadata",
        "get_authors",
        "get_tools",
        "get_projects",
    )
    filter_horizontal = (
        "authors",
        "tools",
        "projects",
    )
    form = PublicationDataForm
    list_filter = [("creator", admin.RelatedOnlyFieldListFilter), ("metadata", admin.RelatedOnlyFieldListFilter)]
    date_hierarchy = "creation_time"

    def get_authors(self, data):
        return data.get_authors()

    def get_tools(self, data):
        return data.get_tools()

    def get_projects(self, data):
        return data.get_projects()


@register(UserPublicationStatus)
class UserPublicationStatusAdmin(admin.ModelAdmin):
    list_display = ["user", "doi", "date_added", "status"]
    form = UserPublicationStatusForm
    list_filter = ["date_added", "status"]
    date_hierarchy = "date_added"
    search_fields = ["doi"]
