from django.core.urlresolvers import reverse_lazy
from django.contrib import messages

from permissionsx.models import P
from permissionsx.models import Permissions
from permissionsx.contrib.django.views import MessageRedirectView

from example.content.models import Article


editor_or_administrator = P(user__is_editor=True) | P(user__is_administrator=True)


class SubscriptionRequiredRedirectView(MessageRedirectView):

    message = (messages.warning, 'You must be signed up to access content!')
    redirect_url = reverse_lazy('account_signup')


class UserPermissions(Permissions):

    rules = P(user__is_authenticated=True, if_false=SubscriptionRequiredRedirectView.as_view())


class AuthorPermissions(Permissions):

    rules = P(user__is_author=True) | editor_or_administrator


class StaffPermissions(Permissions):

    rules = editor_or_administrator


class AdministratorPermissions(Permissions):

    rules = P(user__is_administrator=True)


class AuthorIfNotPublishedPermissions(Permissions):

    def get_rules(self, request=None, **kwargs):
        try:
            request.article = Article.objects.get(slug=kwargs.get('slug'))
        except Article.DoesNotExist:
            request.article = None
        return editor_or_administrator | P(P(user__is_author=True) & P(article__is_published=False) & P(article__author=request.user))
