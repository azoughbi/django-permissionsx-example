from django.views.generic import (
    DetailView,
    ListView,
    TemplateView,
)
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect

from permissionsx.contrib.django.views import (
    PermissionsCreateView,
    PermissionsDeleteView,
    PermissionsDetailView,
    PermissionsListView,
    PermissionsUpdateView,
    PermissionsTemplateView,
)

from example.profiles.permissions import (
    AuthorPermissions,
    AuthorIfNotPublishedPermissions,
    StaffPermissions,
    UserPermissions,
)
from example.content.models import (
    Article,
    Topic,
)
from example.content.forms import (
    ArticleAuthorAddEditForm,
    ArticlePublisherAddEditForm,
)


class FrontpageView(TemplateView):

    template_name = 'content/frontpage.html'

    def get_context_data(self, **kwargs):
        context_data = super(FrontpageView, self).get_context_data(**kwargs)
        context_data['last_article'] = Article.objects.latest()
        return context_data


class ArticleAuthoredListView(PermissionsListView):

    model = Article
    template_name = 'content/article_authored.html'
    permissions = AuthorPermissions()

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)


class ArticlePendingListView(PermissionsListView):

    model = Article
    template_name = 'content/article_pending.html'
    permissions = StaffPermissions()

    def get_queryset(self):
        return self.model.objects.filter(is_pending=True)


class ArticlePublishedListView(PermissionsListView):

    model = Article
    template_name = 'content/article_published.html'
    permissions = StaffPermissions()

    def get_queryset(self):
        return self.model.objects.filter(is_published=True)


class ArticleCreateView(PermissionsCreateView):

    model = Article
    success_url = reverse_lazy('article_authored')
    permissions = AuthorPermissions()

    def get_form_class(self):
        if self.request.user.is_author:
            return ArticleAuthorAddEditForm
        else:
            return ArticlePublisherAddEditForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class ArticleUpdateView(PermissionsUpdateView):

    model = Article
    success_url = reverse_lazy('article_authored')
    permissions = AuthorIfNotPublishedPermissions()

    def get_form_class(self):
        if self.request.user.is_author:
            return ArticleAuthorAddEditForm
        else:
            return ArticlePublisherAddEditForm

    def form_valid(self, form):
        messages.success(self.request, 'Article "%s" updated successfully!' % self.object.title)
        return super(ArticleUpdateView, self).form_valid(form)


class ArticleDeleteView(PermissionsDeleteView):

    model = Article
    template_name = 'delete.html'
    success_url = reverse_lazy('article_authored')
    permissions = AuthorIfNotPublishedPermissions()

    def post(self, *args, **kwargs):
        if 'cancel' in self.request.POST:
            return HttpResponseRedirect(reverse('article_authored'))
        else:
            messages.success(self.request, 'Article deleted successfully!')
            return self.delete(*args, **kwargs)


class ArticleDetailView(PermissionsDetailView):

    model = Article
    permissions = UserPermissions()

    def get_queryset(self):
        return self.model._default_manager.filter(is_published=True)


class TopicManagementView(PermissionsTemplateView):

    template_name = 'content/topic_management.html'
    permissions = StaffPermissions()


class TopicDetailView(DetailView):

    model = Topic
    template_name = 'content/topic_detail.html'


class TopicListView(ListView):

    queryset = Topic.objects.all().order_by('label')

