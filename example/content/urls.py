from django.conf.urls import patterns, include, url

from example.content.views import (
    ArticleAuthoredListView,
    ArticleCreateView,
    ArticleDeleteView,
    ArticleDetailView,
    ArticlePendingListView,
    ArticlePublishedListView,
    ArticleUpdateView,
    FrontpageView,
    TopicDetailView,
    TopicListView,
    TopicManagementView,
)


urlpatterns = patterns('',
    url(r'^$', FrontpageView.as_view(), name='home'),
    url(r'^articles/authored.html$', ArticleAuthoredListView.as_view(), name='article_authored'),
    url(r'^articles/pending.html$', ArticlePendingListView.as_view(), name='article_pending'),
    url(r'^articles/published.html$', ArticlePublishedListView.as_view(), name='article_published'),
    url(r'^article/create.html$', ArticleCreateView.as_view(), name='article_create'),
    url(r'^article/(?P<slug>[a-z0-9-_]+)/update.html$', ArticleUpdateView.as_view(), name='article_update'),
    url(r'^article/(?P<slug>[a-z0-9-_]+)/delete.html$', ArticleDeleteView.as_view(), name='article_delete'),
    url(r'^article/(?P<slug>[a-z0-9-_]+).html$', ArticleDetailView.as_view(), name='article_detail'),
    url(r'^topics/management.html$', TopicManagementView.as_view(), name='topic_management'),
    url(r'^topic/(?P<slug>[a-z0-9-_]+).html$', TopicDetailView.as_view(), name='topic_detail'),
    url(r'^topics.html$', TopicListView.as_view(), name='topic_list'),
)
