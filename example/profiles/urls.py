from django.conf.urls import patterns, include, url

from example.profiles.views import *


urlpatterns = patterns('',
    url(r'^profile/(?P<slug>[a-z0-9-_]+).html$', AuthorDetailView.as_view(), name='author_detail'),
    url(r'^authors.html$', AuthorListView.as_view(), name='author_browse'),
    url(r'^account/users.html$', ProfileListView.as_view(), name='profile_list'),
    url(r'^account/user/create.html$', ProfileCreateView.as_view(), name='profile_create'),
    url(r'^account/user/(?P<pk>\d+)/update.html$', ProfileUpdateView.as_view(), name='profile_update'),
    url(r'^account/user/(?P<pk>\d+)/delete.html$', ProfileDeleteView.as_view(), name='profile_delete'),
    url(r'^account/settings_change.html$', ProfileSettingsUpdateView.as_view(), name='profile_settings'),
    url(r'^account/avatar_change.html$', AvatarChangeView.as_view(), name='avatar_change'),
    url(r'^render_primary/(?P<user>[\w\d\.\-_]{3,30})/(?P<size>[\d]+)/$', 'render_primary', name='avatar_render_primary'),
    url(r'^list/(?P<username>[\+\w\@\.]+)/$', 'avatar_gallery', name='avatar_gallery'),
    url(r'^list/(?P<username>[\+\w\@\.]+)/(?P<id>[\d]+)/$', 'avatar', name='avatar'),
)
