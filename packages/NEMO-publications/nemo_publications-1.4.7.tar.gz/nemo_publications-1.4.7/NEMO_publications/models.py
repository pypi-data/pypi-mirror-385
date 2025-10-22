from datetime import MAXYEAR, date

from NEMO.models import BaseModel, Project, Tool, User
from NEMO.views.constants import CHAR_FIELD_MAXIMUM_LENGTH
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from NEMO_publications.notifications import delete_publication_notification, manage_publication_notification
from NEMO_publications.utils import sanitize_doi, parse_bibtex


class Months(models.IntegerChoices):
    JAN = 1, "JANUARY"
    FEB = 2, "FEBRUARY"
    MAR = 3, "MARCH"
    APR = 4, "APRIL"
    MAY = 5, "MAY"
    JUN = 6, "JUNE"
    JUL = 7, "JULY"
    AUG = 8, "AUGUST"
    SEP = 9, "SEPTEMBER"
    OCT = 10, "OCTOBER"
    NOV = 11, "NOVEMBER"
    DEC = 12, "DECEMBER"


class PublicationMetadataStatus(object):
    APPROVED = 1
    REJECTED = 2
    Choices = (
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    )


class PublicationMetadata(BaseModel):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_time = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time when the publication metadata was created.",
    )
    doi = models.CharField(
        max_length=CHAR_FIELD_MAXIMUM_LENGTH,
        help_text="Digital Object Identifier (DOI) of the publication.",
        unique=True,
    )
    title = models.CharField(
        max_length=CHAR_FIELD_MAXIMUM_LENGTH,
        help_text="Title of the publication.",
    )
    journal = models.CharField(
        max_length=CHAR_FIELD_MAXIMUM_LENGTH,
        help_text="Journal where the publication is published.",
    )
    bibtex = models.TextField(
        null=True,
        blank=True,
        help_text="Publication bibtex metadata.",
    )
    json_metadata = models.TextField(
        null=True,
        blank=True,
        help_text="Publication json metadata.",
    )
    year = models.PositiveIntegerField(
        help_text="Publication year.", validators=[MinValueValidator(1900), MaxValueValidator(MAXYEAR)]
    )
    month = models.PositiveIntegerField(null=True, blank=True, choices=Months.choices, help_text="Publication month.")
    image_url = models.URLField(null=True, blank=True, help_text="Publication image URL.")
    status = models.IntegerField(
        choices=PublicationMetadataStatus.Choices,
        null=True,
        blank=True,
        help_text="Publication metadata status.",
    )
    decision_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date and time when the publication metadata was approved or rejected.",
    )

    def get_doi_url(self):
        return "https://doi.org/" + self.doi

    def get_date(self) -> date:
        return date(year=self.year, month=self.month or 1, day=1)

    def get_authors(self, exclude=None):
        publication_data = self.publicationdata_set.all()
        if exclude:
            publication_data = publication_data.exclude(id__in=exclude)
        return set([author for pub in publication_data for author in pub.authors.all()])

    def get_projects(self, exclude=None):
        publication_data = self.publicationdata_set.all()
        if exclude:
            publication_data = publication_data.exclude(id__in=exclude)
        return set([project for pub in publication_data for project in pub.projects.all()])

    def get_tools(self, exclude=None):
        publication_data = self.publicationdata_set.all()
        if exclude:
            publication_data = publication_data.exclude(id__in=exclude)
        return set([tool for pub in publication_data for tool in pub.tools.all()])

    def get_related_data(self, exclude=None):
        return {
            "authors": self.get_authors(exclude),
            "tools": self.get_tools(exclude),
            "projects": self.get_projects(exclude),
        }

    def get_data_creators(self):
        data_creator_ids = self.publicationdata_set.values_list("creator").distinct()
        return User.objects.filter(id__in=data_creator_ids)

    def get_bibtex_fields(self):
        if self.bibtex:
            return parse_bibtex(self.bibtex)

    def get_bibtex_authors(self):
        parsed_bibtex = self.get_bibtex_fields()
        if parsed_bibtex:
            return parsed_bibtex.get("author") or parsed_bibtex.get("authors")

    def __str__(self):
        return self.title + " (" + self.doi + ")"

    def clean(self):
        self.doi = self.doi.upper()


class PublicationData(BaseModel):
    creator = models.ForeignKey(User, related_name="publication_data_creator", on_delete=models.CASCADE)
    creation_time = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time when the publication data was created.",
    )
    metadata = models.ForeignKey(
        PublicationMetadata,
        null=False,
        help_text="The metadata of the publication",
        on_delete=models.CASCADE,
    )
    authors = models.ManyToManyField(User, blank=True, help_text="Authors of the publication.")
    tools = models.ManyToManyField(Tool, blank=True, help_text="Tools involved in the publication.")
    projects = models.ManyToManyField(Project, blank=True, help_text="Projects involved in the publication.")

    def get_authors(self):
        return ", ".join([author.__str__() for author in self.authors.all()])

    def get_projects(self):
        return ", ".join([project.__str__() for project in self.projects.all()])

    def get_tools(self):
        return ", ".join([tool.__str__() for tool in self.tools.all()])


class PublicationDataM2MValidationError(Exception):
    def __init__(self, message):
        self.message = message


def validation_publication_data_m2m(data, creator):
    # Check that at least one of authors, projects, tools is specified
    if not data["authors"].exists() and not data["projects"].exists() and not data["tools"].exists():
        raise PublicationDataM2MValidationError("At least one author, project or tool is required.")
    # check that the creator is part of the projects added to the list
    if creator:
        if (
            data["projects"].exists()
            and not data["projects"].filter(Q(user=creator) | Q(manager_set=creator)).exists()
            and not creator.is_any_part_of_staff
        ):
            projects_str = ", ".join(
                [
                    project.__str__()
                    for project in data["projects"].exclude(Q(user=creator) | Q(manager_set=creator)).all()
                ]
            )
            raise PublicationDataM2MValidationError(
                {"projects": "You cannot add project(s): " + projects_str + " to the publication."}
            )


class UserPublicationStatus(BaseModel):
    class Status(models.IntegerChoices):
        PENDING = 1, "Pending"
        ADDED = 2, "Added"
        REJECTED = 3, "Rejected"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="publication_statuses")
    doi = models.CharField(max_length=CHAR_FIELD_MAXIMUM_LENGTH)
    date_added = models.DateTimeField(auto_now_add=True)
    status = models.PositiveIntegerField(choices=Status.choices, default=Status.PENDING)

    class Meta:
        unique_together = ("user", "doi")
        verbose_name_plural = "User publication statuses"

    def save(self, *args, **kwargs):
        self.doi = sanitize_doi(self.doi)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.doi} - {self.get_status_display()}"


@receiver(m2m_changed, sender=PublicationData.authors.through)
def handle_publication_authors_save(sender, instance: PublicationData, action, **kwargs):
    if action == "post_add":
        for pub_author in instance.authors.all():
            for user_publication in UserPublicationStatus.objects.filter(
                user=pub_author, doi=instance.metadata.doi, status=UserPublicationStatus.Status.PENDING
            ):
                user_publication.status = UserPublicationStatus.Status.ADDED
                user_publication.save(update_fields=["status"])


@receiver(post_save, sender=UserPublicationStatus)
def handle_user_publication_status_save(sender, instance, **kwargs):
    manage_publication_notification(instance)


@receiver(post_delete, sender=UserPublicationStatus)
def handle_user_publication_status_delete(sender, instance, **kwargs):
    delete_publication_notification(instance)
