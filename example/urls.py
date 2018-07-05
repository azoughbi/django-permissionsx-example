from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static

from tastypie.api import Api

from example.content.api import (
    ArticleCommentsResource,
    ArticleResource,
    CommentResource,
    TopicResource,
)


v1_api = Api(api_name='v1')
v1_api.register(CommentResource())
v1_api.register(ArticleCommentsResource())
v1_api.register(TopicResource())
v1_api.register(ArticleResource())


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^', include('example.content.urls')),
    url(r'^', include('example.profiles.urls')),
    url(r'^account/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
    url(r'^tinymce/', include('tinymce.urls')),
)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
