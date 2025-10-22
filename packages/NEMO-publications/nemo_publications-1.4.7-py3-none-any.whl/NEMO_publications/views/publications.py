import json
import math
from typing import Optional
from urllib.parse import urlparse

from NEMO.decorators import staff_member_required
from NEMO.models import Project, Tool, User
from NEMO.typing import QuerySetType
from NEMO.utilities import (
    BasicDisplayTable,
    export_format_datetime,
    queryset_search_filter,
    quiet_int,
    render_combine_responses,
)
from NEMO.views.landing import landing
from NEMO.views.notifications import get_notifications
from NEMO.views.pagination import SortedPaginator
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from NEMO_publications.customization import PublicationsCustomization
from NEMO_publications.forms import (
    PublicationDataForm,
    create_publication_data_post_form,
    create_publication_metadata_post_form,
)
from NEMO_publications.models import PublicationData, PublicationMetadata, PublicationMetadataStatus
from NEMO_publications.utils import (
    PUBLICATION_NOTIFICATION,
    fetch_publication_metadata_by_doi,
)
from NEMO_publications.models import UserPublicationStatus


@login_required
@require_GET
def new_landing(request):
    original_view = landing(request)
    if PublicationsCustomization.get_bool("publications_enable_landing_carousel") or PublicationsCustomization.get_bool(
        "publications_enable_landing_warning_pending_publications"
    ):
        return render_combine_responses(
            request,
            original_view,
            "NEMO_publications/new_landing.html",
            {"publication_notifications": get_notifications(request.user, PUBLICATION_NOTIFICATION, delete=False)},
        )
    else:
        return original_view


@login_required
@require_GET
def user_search(request):
    return queryset_search_filter(User.objects.all(), ["first_name", "last_name", "username"], request)


@staff_member_required
@require_POST
def set_publication_status(request, publication_metadata_id):
    publication_metadata = get_object_or_404(PublicationMetadata, id=publication_metadata_id)
    decision_option = [state for state in ["approve", "reject"] if state in request.POST]
    decision = decision_option[0] if len(decision_option) == 1 else None
    if publication_metadata.status:
        return HttpResponseBadRequest("Publication metadata status is already set")
    if decision and not publication_metadata.status:
        if decision == "approve":
            publication_metadata.status = PublicationMetadataStatus.APPROVED
        elif decision == "reject":
            publication_metadata.status = PublicationMetadataStatus.REJECTED
        publication_metadata.decision_time = timezone.now()
        publication_metadata.save()
    return HttpResponse()


@login_required
@require_http_methods(["GET", "POST"])
def create_or_update_publication_data(request, publication_data_id=None, publication_metadata_id=None):
    user: User = request.user
    dictionary = {}

    # Initialize publication data (found: edit, not found: create) and publication metadata (mandatory)
    try:
        publication_data = PublicationData.objects.get(id=publication_data_id)
        publication_metadata = PublicationMetadata.objects.get(id=publication_data.metadata.id)
    except PublicationData.DoesNotExist:
        publication_data = PublicationData()
        # Initialize publication metadata from POST["metadata_id"] - when creating a new publication data entry
        if publication_metadata_id:
            publication_metadata = PublicationMetadata.objects.get(id=publication_metadata_id)
        else:
            return HttpResponseBadRequest("Publication metadata not found.")
    except PublicationMetadata.DoesNotExist:
        return HttpResponseBadRequest("Publication metadata is invalid.")

    if publication_metadata.status == PublicationMetadataStatus.REJECTED:
        return HttpResponseBadRequest("You cannot edit this publication.")

    if request.method == "POST":
        edit = bool(publication_data.id)
        # Only creator can edit publication_data
        if edit and publication_data.creator != user:
            return HttpResponseNotFound("Publication data not found.")
        form = create_publication_data_post_form(request, user, edit, publication_data)
        # Initialize creator and metadata - when creating a new publication data entry
        if not edit:
            form.instance.creator = user
            form.instance.metadata = publication_metadata

        # Only save if the user is actually adding new info. Unless we don't already have at least on publication
        if (
            not "authors" in form.data and not "projects" in form.data and not "tools" in form.data
        ) and publication_metadata.publicationdata_set.exclude(id=publication_data.id).exists():
            return redirect("publications")
        if form.is_valid():
            form.save()
            if (
                not edit
                and UserPublicationStatus.objects.filter(
                    user=user, status=UserPublicationStatus.Status.PENDING
                ).exists()
            ):
                return redirect("search_publication")
            return redirect("publications")
        else:
            dictionary["form"] = form
            return edit_publication_data(
                request, publication_metadata, dictionary, user, [publication_data.id] if edit else None
            )
    else:
        form = PublicationDataForm(instance=publication_data)
        dictionary["form"] = form
        return edit_publication_data(
            request, publication_metadata, dictionary, user, [publication_data.id] if publication_data.id else None
        )


@login_required
@require_POST
def create_publication_metadata(request):
    user: User = request.user
    metadata_form = create_publication_metadata_post_form(request.POST, user, PublicationMetadata())
    # Can only create publication metadata once, prevent if DOI already exists
    doi = request.POST.get("doi")
    if doi and PublicationMetadata.objects.filter(doi__iexact=doi).exists():
        metadata_form.add_error(None, ["Publication metadata already exists."])
    metadata_form.instance.creator = user
    metadata_form.instance.bibtex = None
    if metadata_form.is_valid():
        publication_metadata = metadata_form.save()
        # Proceed to show publication data form once metadata saved
        return edit_publication_data(
            request,
            publication_metadata,
            {},
            user,
        )
    else:
        return render(request, "NEMO_publications/publication_metadata.html", {"form": metadata_form})


@login_required
@require_http_methods(["GET", "POST"])
def search_publication_by_doi(request):
    user: User = request.user
    user_publications = UserPublicationStatus.objects.filter(user=user, status=UserPublicationStatus.Status.PENDING)
    if request.method == "POST":
        # DOI is required for search
        doi = request.POST.get("doi")
        if not doi:
            return render(request, "NEMO_publications/publication_search.html", {"error": "DOI is missing"})
        # Remove scheme from doi URL if provided, so we only keep the actual DOI
        parsed_url = urlparse(doi)
        doi = parsed_url.geturl().replace("%s://doi.org/" % parsed_url.scheme, "", 1)
        try:
            # Lookup publication metadata first in database using DOI
            publication_metadata = PublicationMetadata.objects.get(doi__iexact=doi)
            # Do not allow to add rejected publication
            if publication_metadata.status == PublicationMetadataStatus.REJECTED:
                return render(
                    request,
                    "NEMO_publications/publication_search.html",
                    {"error": "You cannot add this publication."},
                )
            try:
                # If the user already has a publication data entry for DOI, redirect to publication data edit
                existing_publication_data = PublicationData.objects.get(
                    metadata__id=publication_metadata.id, creator=user
                )
                return redirect("edit_publication", existing_publication_data.id)
            except PublicationData.DoesNotExist:
                return edit_publication_data(
                    request,
                    publication_metadata,
                    {"form": PublicationDataForm(instance=PublicationData())},
                    user,
                )
        except PublicationMetadata.DoesNotExist:
            # If metadata for DOI does not exist in DB, fetch from remote
            publication_metadata_form = fetch_publication_metadata_as_form(doi, user)
            # Always show form so the user can set the image URL if they want
            return render(
                request,
                "NEMO_publications/publication_metadata.html",
                {
                    "form": publication_metadata_form,
                    "user_publication": get_user_publication(user, doi),
                },
            )
    else:
        return render(request, "NEMO_publications/publication_search.html", {"user_publications": user_publications})


def fetch_publication_metadata_as_form(doi, user):
    publication_metadata_search = fetch_publication_metadata_by_doi(doi)
    publication_metadata_form = create_publication_metadata_post_form(
        publication_metadata_search["metadata"], user, PublicationMetadata()
    )
    publication_metadata_form.instance.creator = user
    if "error" in publication_metadata_search.keys():
        publication_metadata_form.add_error(None, [publication_metadata_search["error"]])
    return publication_metadata_form


@login_required
@require_GET
def get_publication_leaderboard(request, year=None):
    current_year = timezone.now().year
    selected_year = quiet_int(year, current_year)
    authors_publication_count = User.objects.annotate(
        publication_count=Count(
            "publicationdata__metadata",
            filter=Q(publicationdata__metadata__year=selected_year)
            & ~Q(publicationdata__metadata__status=PublicationMetadataStatus.REJECTED),
        )
    ).filter(publication_count__gt=0)

    page = SortedPaginator(authors_publication_count, request, order_by="-publication_count").get_current_page()
    years = list(PublicationData.objects.values_list("metadata__year", flat=True).distinct())

    if current_year not in years:
        years.insert(0, current_year)
    years.sort(reverse=True)

    return render(
        request,
        "NEMO_publications/leaderboard.html",
        {
            "page": page,
            "selected_year": selected_year,
            "years": years,
            "publication_notifications": get_notifications(request.user, PUBLICATION_NOTIFICATION, delete=False),
        },
    )


@login_required
@require_GET
def get_publications(request):
    user: User = request.user
    # Get all publications that have data entries
    publications_with_data = (
        PublicationMetadata.objects.exclude(publicationdata=None)
        .exclude(status=PublicationMetadataStatus.REJECTED)
        .prefetch_related(
            "publicationdata_set",
            "publicationdata_set__authors",
            "publicationdata_set__projects",
            "publicationdata_set__tools",
        )
    )

    selected_tool = Tool.objects.filter(id=request.GET.get("selected_tool") or None).first()
    selected_project = Project.objects.filter(id=request.GET.get("selected_project") or None).first()
    selected_author = User.objects.filter(id=request.GET.get("selected_author") or None).first()

    if selected_author:
        publications_with_data = publications_with_data.filter(publicationdata__authors__in=[selected_author])
    if selected_tool:
        publications_with_data = publications_with_data.filter(publicationdata__tools__in=[selected_tool])
    if selected_project:
        publications_with_data = publications_with_data.filter(publicationdata__projects__in=[selected_project])

    page = SortedPaginator(publications_with_data, request, order_by="-creation_time").get_current_page()

    if bool(request.GET.get("csv", False)) and user.is_any_part_of_staff:
        return export_publications(publications_with_data.order_by("-creation_time"))

    # Create dictionary associating each publication metadata id with the user's data entry
    user_publication_data = PublicationData.objects.filter(creator=user, metadata__in=page)
    user_publication_data_dict = {}
    for user_publication_data in user_publication_data:
        user_publication_data_dict[user_publication_data.metadata_id] = user_publication_data

    return render(
        request,
        "NEMO_publications/publications.html",
        {
            "page": page,
            "user_data": user_publication_data_dict,
            "projects": get_json_project_search_list(user),
            "tools": Tool.objects.all(),
            "selected_tool": selected_tool,
            "selected_author": selected_author,
            "selected_project": selected_project,
            "publication_notifications": get_notifications(request.user, PUBLICATION_NOTIFICATION, delete=False),
        },
    )


@login_required
@require_POST
def delete_publication(request, publication_data_id):
    user = request.user
    # Lookup and delete the user's data entry
    publication = get_object_or_404(PublicationData, pk=publication_data_id)
    if publication.creator != user:
        return HttpResponseBadRequest("You are not allowed to delete this publication data")
    publication.delete()
    return redirect("publications")


def edit_publication_data(request, metadata, dictionary, user, other_users_exclude_data=None):
    dictionary["metadata"] = metadata
    dictionary["projects"] = get_json_project_search_list(user)
    dictionary["tools"] = Tool.objects.all()
    dictionary["authors_suggestion"] = metadata.get_bibtex_authors()
    dictionary["other_users"] = metadata.get_related_data(other_users_exclude_data)
    dictionary["user_publication"] = get_user_publication(user, metadata.doi)
    return render(request, "NEMO_publications/publication_data.html", dictionary)


def get_json_project_search_list(user):
    projects = Project.objects.all().prefetch_related("manager_set")
    if not user.is_any_part_of_staff:
        projects = Project.objects.filter(Q(user=user) | Q(manager_set=user))

    search_list = []
    for project in projects:
        search_list.append(
            {
                "id": project.id,
                "name": project.__str__(),
                "pis": [{"id": pi.id, "name": pi.__str__()} for pi in project.manager_set.all()],
            }
        )
    return mark_safe(json.dumps(search_list))


def export_publications(publication_list: QuerySetType[PublicationMetadata]):
    table = get_publications_table_display(publication_list)
    filename = f"publications_{export_format_datetime()}.csv"
    response = table.to_csv()
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def get_publications_table_display(publication_list: QuerySetType[PublicationMetadata]) -> BasicDisplayTable:
    table = BasicDisplayTable()
    table.add_header(("title", "Title"))
    table.add_header(("journal", "Journal"))
    table.add_header(("year", "Year"))
    table.add_header(("doi", "DOI"))
    table.add_header(("authors", "Authors"))
    table.add_header(("tools", "Tools"))
    table.add_header(("projects", "Projects"))
    table.add_header(("metadata_creators", "Metadata Created By"))
    table.add_header(("data_creators", "Data Created By"))
    table.add_header(("bibtex", "Bibtex"))
    for metadata in publication_list:
        row = {
            "title": metadata.title,
            "journal": metadata.journal,
            "year": metadata.year,
            "doi": metadata.doi,
            "authors": ", ".join([author.__str__() for author in metadata.get_authors()]),
            "tools": ", ".join([tool.__str__() for tool in metadata.get_tools()]),
            "projects": ", ".join([project.__str__() for project in metadata.get_projects()]),
            "metadata_creators": metadata.creator.__str__(),
            "data_creators": ", ".join([project.__str__() for project in metadata.get_data_creators()]),
            "bibtex": metadata.bibtex,
        }
        table.add_row(row)
    return table


@login_required
@require_GET
def carousel_content(request, content: str = "mixed"):
    selected_year = timezone.now().year
    # Find the first 2 years (going backwards from today) with publications (check 5 years total)
    publication_counts = []
    for year in range(selected_year, selected_year - 5, -1):
        publication_count = (
            User.objects.annotate(
                publication_count=Count(
                    "publicationdata__metadata",
                    filter=Q(publicationdata__metadata__year=year)
                    & ~Q(publicationdata__metadata__status=PublicationMetadataStatus.REJECTED),
                )
            )
            .order_by("-publication_count")
            .filter(publication_count__gt=0)[:5]
        )
        if publication_count:
            publication_counts.append((year, publication_count))
        if len(publication_counts) == 2:
            break
    number_of_latest_pub_to_display = PublicationsCustomization.get_int("publications_carousel_latest_display_count")
    publication_order = json.loads(PublicationsCustomization.get("publications_carousel_latest_display_order"))
    latest_publications = (
        PublicationMetadata.objects.exclude(publicationdata__isnull=True)
        .prefetch_related(
            "publicationdata_set",
            "publicationdata_set__authors",
            "publicationdata_set__projects",
            "publicationdata_set__tools",
        )
        .exclude(status=PublicationMetadataStatus.REJECTED)
        .order_by(*publication_order)[:number_of_latest_pub_to_display]
    )
    is_coming_from_landing = request.META.get("HTTP_REFERER") == request.build_absolute_uri(reverse("landing"))
    return render(
        request,
        "NEMO_publications/carousel.html",
        {
            "publication_counts": publication_counts,
            "publications": latest_publications,
            "show_pub_date": PublicationsCustomization.get_bool("publications_carousel_show_date"),
            "show_pub_authors": PublicationsCustomization.get_bool("publications_carousel_show_authors"),
            "show_pub_tools": PublicationsCustomization.get_bool("publications_carousel_show_tools"),
            "show_pub_projects": PublicationsCustomization.get_bool("publications_carousel_show_projects"),
            "img_max_height": "150" if is_coming_from_landing else None,
            **get_carousel_parameters(latest_publications.count(), content),
        },
    )


def get_carousel_parameters(number_of_results, content):
    number_of_latest_pub_to_display = PublicationsCustomization.get_int("publications_carousel_latest_display_count")
    interval_time_in_ms = PublicationsCustomization.get_int("publications_carousel_interval_time") * 1000
    tiles_per_item = PublicationsCustomization.get_int("publications_carousel_tiles_per_item", default=2)
    # we show them by pairs, so divide by 2 + 1 for the first item (leaderboard)
    items = 0
    if content in ["leaderboard", "mixed"]:
        items += 1
    if content in ["publications", "mixed"]:
        items += math.ceil(min(number_of_latest_pub_to_display, number_of_results) / tiles_per_item)
    refresh_time = items * interval_time_in_ms
    return {
        "interval_time": interval_time_in_ms,
        "refresh_time": refresh_time,
        "tiles_per_item": tiles_per_item,
        "item_grid_size": int(12 / tiles_per_item),
        "content": content,
    }


@login_required
@require_GET
def jumbotron(request, content: str = "mixed"):
    return render(request, "NEMO_publications/jumbotron.html", get_carousel_parameters(0, content))


def get_user_publication(user: User, doi: str) -> Optional[UserPublicationStatus]:
    return (
        UserPublicationStatus.objects.filter(user=user, status=UserPublicationStatus.Status.PENDING)
        .filter(doi__iexact=doi)
        .first()
    )


@login_required
@require_GET
def reject_user_publication(request, user_publication_status_id: int):
    user_pub = get_object_or_404(UserPublicationStatus, id=user_publication_status_id)
    if user_pub.status == UserPublicationStatus.Status.PENDING:
        user_pub.status = UserPublicationStatus.Status.REJECTED
        user_pub.save(update_fields=["status"])
    if UserPublicationStatus.objects.filter(user=user_pub.user, status=UserPublicationStatus.Status.PENDING).exists():
        return redirect("search_publication")
    return redirect("publications")
