from django.db import models
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)

from autoslug import AutoSlugField


MAP_ROLES = (
    (1, 'author'),
    (2, 'editor'),
    (3, 'administrator'),
)


class ProfileQuerySet(models.query.QuerySet):

    def authors(self):
        return self.filter(articles__isnull=False).distinct().order_by('last_name')

    def signed_up(self):
        return self.filter(is_signed_up=True)


class ProfileManager(models.Manager):

    def authors(self):
        return self.get_query_set().authors()

    def signed_up(self):
        return self.get_query_set().signed_up()

    def get_query_set(self):
        return ProfileQuerySet(self.model, using=self._db)


class Profile(AbstractUser):

    user_role = models.SmallIntegerField(choices=MAP_ROLES, null=True, blank=True)
    slug = AutoSlugField(unique=True, populate_from='full_name')
    about_me = models.TextField(blank=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    objects = BaseUserManager()
    shortcuts = ProfileManager()

    @property
    def is_author(self):
        return self.user_role == 1

    @property
    def is_editor(self):
        return self.user_role == 2

    @property
    def is_administrator(self):
        return self.user_role == 3

    @property
    def full_name(self):
        return self.get_full_name()

    @models.permalink
    def get_absolute_url(self):
        return ('author_detail', [str(self.slug)])

    def __unicode__(self):
        return self.full_name
