import base64

from django.core.files.uploadedfile import SimpleUploadedFile

import bleach
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.exceptions import Unauthorized
from mptt.templatetags.mptt_tags import cache_tree_children
from avatar.templatetags.avatar_tags import avatar_url
from permissionsx.contrib.tastypie import TastypieAuthorization

from example.profiles.permissions import (
    UserPermissions,
    StaffPermissions,
)
from example.content.models import (
    Article,
    Comment,
    Topic,
)


class StaffOnlyAuthorization(TastypieAuthorization):

    permissions = StaffPermissions()


class CommentingAuthorization(TastypieAuthorization):

    permissions = UserPermissions()

    def create_list(self, object_list, bundle):
        raise Unauthorized()

    def update_list(self, object_list, bundle):
        raise Unauthorized()

    def update_detail(self, object_list, bundle):
        return StaffPermissions().check(bundle.request)

    def delete_list(self, object_list, bundle):
        raise Unauthorized()

    def delete_detail(self, object_list, bundle):
        raise Unauthorized()


class DataBase64FileField(fields.FileField):

    def hydrate(self, obj):
        value = super(DataBase64FileField, self).hydrate(obj)
        try:
            data_header, content = value.split(';base64,')
        except (ValueError, AttributeError):
            # NOTE: Quite nasty shortcut. Submitted form did not change (at least
            #       that is assumed), because it returns original value (file path).
            #       Otherwise that would contain Data-URI encoded file.
            return value
        else:
            content_type = data_header[5:]
            return SimpleUploadedFile('icon.jpg', base64.b64decode(content), content_type=content_type)
        return None


class ArticleResource(ModelResource):

    class Meta:
        authorization = StaffOnlyAuthorization()
        queryset = Article.objects.exclude(title='').exclude(is_published=False)
        include_resource_uri = False
        fields = ('id', 'title')
        max_limit = None


class TopicResource(ModelResource):

    icon = DataBase64FileField('icon', null=True, blank=True)
    parent = fields.ToOneField('self', 'parent', null=True)

    class Meta:
        authorization = StaffOnlyAuthorization()
        queryset = Topic.objects.all().select_related('parent')
        include_resource_uri = False
        fields = ('label', 'icon')
        max_limit = None

    def get_child_data(self, obj):
        data = {
            'id': obj.id,
            'label': obj.label,
            'icon': obj.icon,
        }
        if not obj.is_leaf_node():
            data['children'] = [self.get_child_data(child) for child in obj.get_children()]
        return data

    def hydrate_parent(self, bundle):
        if 'parent' in bundle.data:
            if bundle.data['parent']:
                bundle.data['parent'] = self.get_via_uri(bundle.data['parent'], bundle.request)
            else:
                bundle.data['parent'] = None
        return bundle

    def get_list(self, request, **kwargs):
        base_bundle = self.build_bundle(request=request)
        objects = self.obj_get_list(bundle=base_bundle, **self.remove_api_resource_names(kwargs))
        objects = cache_tree_children(objects)
        bundles = []
        for obj in objects:
            data = self.get_child_data(obj)
            bundle = self.build_bundle(data=data, obj=obj, request=request)
            bundles.append(self.full_dehydrate(bundle))
        return self.create_response(request, bundles)


class CommentResource(ModelResource):

    class Meta:
        queryset = Comment.objects.filter(is_blocked=False)
        include_resource_uri = False
        authorization = CommentingAuthorization()
        fields = ('content', 'id', 'is_blocked')
        max_limit = None

    def obj_create(self, bundle, **kwargs):
        bundle.obj = Comment()
        bundle.obj.article_id = bundle.data['article']
        bundle.obj.user = bundle.request.user
        bundle.obj.content = bleach.clean(bundle.data['content'], tags=())
        return self.save(bundle)

    def dehydrate(self, bundle):
        bundle.data['full_name'] = bundle.obj.user.full_name
        bundle.data['profile_url'] = bundle.obj.user.get_absolute_url()
        bundle.data['avatar_url'] = avatar_url(bundle.obj.user)
        return bundle


class ArticleCommentsResource(ModelResource):

    comments = fields.ToManyField('example.content.api.CommentResource', lambda bundle: Comment.objects.filter(is_blocked=False), full=True, null=True)

    class Meta:
        queryset = Article.objects.filter(is_published=True)
        include_resource_uri = False
        authorization = CommentingAuthorization()
        resource_name = 'article-comments'
        max_limit = None

    @classmethod
    def get_fields(cls, fields=None, excludes=None):
        return ()
