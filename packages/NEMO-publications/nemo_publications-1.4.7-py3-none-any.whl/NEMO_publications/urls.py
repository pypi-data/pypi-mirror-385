from NEMO.urls import router, sort_urls
from django.urls import path, re_path

from NEMO_publications import api
from NEMO_publications.views import publications

router.register(r"publications/publication_metadata", api.PublicationMetadataViewSet)
router.register(r"publications/publication_data", api.PublicationDataViewSet)
router.register(r"publications/publications", api.PublicationViewSet, basename="publication")
router.register(r"publications/user_publication_status", api.UserPublicationStatusViewSet)
router.registry.sort(key=sort_urls)

urlpatterns = [
    path("", publications.new_landing, name="landing"),
    path(
        "search_publication/",
        publications.search_publication_by_doi,
        name="search_publication",
    ),
    path(
        "edit_publication/<int:publication_data_id>/",
        publications.create_or_update_publication_data,
        name="edit_publication",
    ),
    path(
        "create_publication/<int:publication_metadata_id>/",
        publications.create_or_update_publication_data,
        name="create_publication",
    ),
    path(
        "save_publication_metadata/",
        publications.create_publication_metadata,
        name="save_publication_metadata",
    ),
    path(
        "delete_publication/<int:publication_data_id>/",
        publications.delete_publication,
        name="delete_publication",
    ),
    path(
        "publication_user_search/",
        publications.user_search,
        name="publication_user_search",
    ),
    path(
        "set_publication_status/<int:publication_metadata_id>/",
        publications.set_publication_status,
        name="set_publication_status",
    ),
    path("publications/", publications.get_publications, name="publications"),
    path(
        "reject_user_publication/<int:user_publication_status_id>/",
        publications.reject_user_publication,
        name="reject_user_publication",
    ),
    path("publications/leaderboard/", publications.get_publication_leaderboard, name="publications_leaderboard"),
    path(
        "publications/leaderboard/<int:year>/",
        publications.get_publication_leaderboard,
        name="publications_leaderboard",
    ),
    re_path(
        r"^publications/carousel_content/(?P<content>leaderboard|publications|mixed)/$",
        publications.carousel_content,
        name="publications_carousel_content",
    ),
    re_path(
        r"^publications/jumbotron/(?P<content>leaderboard|publications|mixed)/$",
        publications.jumbotron,
        name="publications_jumbotron",
    ),
    path("publications/jumbotron/", publications.jumbotron, name="publications_jumbotron"),
]
