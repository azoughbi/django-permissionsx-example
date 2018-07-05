import datetime

from django.db import models
from django.conf import settings

from autoslug import AutoSlugField
from mptt.models import (
    MPTTModel,
    TreeForeignKey,
)


class ArticleQuerySet(models.query.QuerySet):

    def published(self):
        return self.filter(is_published=True)


class ArticleManager(models.Manager):

    def published(self):
        return self.get_query_set().published()

    def get_query_set(self):
        return ArticleQuerySet(self.model, using=self._db)


class Article(models.Model):

    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='articles', null=True)
    topic = models.ForeignKey('content.Topic', null=True, on_delete=models.SET_NULL, related_name='articles')
    title = models.CharField(max_length=50)
    slug = AutoSlugField(unique=True, populate_from='title')
    lead = models.CharField(max_length=200)
    content = models.TextField()
    is_pending = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)
    published_datetime = models.DateTimeField(null=True, blank=True)

    objects = ArticleManager()

    class Meta:
        get_latest_by = 'published_datetime'

    @models.permalink
    def get_absolute_url(self):
        return ('article_detail', [str(self.slug)])

    def save(self, *args, **kwargs):
        if self.is_published:
            self.is_pending = False
            if not self.published_datetime:
                self.published_datetime = datetime.datetime.now()
        super(Article, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title


class Topic(MPTTModel):

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    label = models.CharField(max_length=50)
    slug = AutoSlugField(unique=True, populate_from='label')
    icon = models.ImageField(upload_to='icons', blank=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['label']

    @models.permalink
    def get_absolute_url(self):
        return ('topic_detail', [str(self.slug)])

    def __unicode__(self):
        return self.label


class Comment(models.Model):

    article = models.ForeignKey('content.Article', related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField()
    is_blocked = models.BooleanField(default=False)
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.content
