from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils import six

from permissionsx.contrib.django.views import (
    PermissionsCreateView,
    PermissionsDeleteView,
    PermissionsDetailView,
    PermissionsListView,
    PermissionsTemplateView,
    PermissionsUpdateView,
)

from avatar.views import _get_avatars
from avatar.forms import PrimaryAvatarForm, UploadAvatarForm
from avatar.models import Avatar
from avatar.signals import avatar_updated

from example.profiles.permissions import (
    AdministratorPermissions,
    UserPermissions,
)
from example.profiles.models import Profile
from example.profiles.forms import (
    ProfileUpdateForm,
    PublishingProfileCreateForm,
    PublishingProfileUpdateForm,
)


class AuthorListView(PermissionsListView):

    model = Profile
    template_name = 'profiles/profile_authors.html'
    permissions = UserPermissions()

    def get_queryset(self):
        return Profile.shortcuts.authors()


class ProfileListView(PermissionsListView):

    model = Profile
    template_name = 'profiles/profile_list.html'
    permissions = AdministratorPermissions()


class ProfileCreateView(PermissionsCreateView):

    model = Profile
    template_name = 'profiles/profile_form.html'
    success_url = reverse_lazy('profile_list')
    form_class = PublishingProfileCreateForm
    permissions = AdministratorPermissions()


class ProfileUpdateView(PermissionsUpdateView):

    model = Profile
    form_class = PublishingProfileUpdateForm
    success_url = reverse_lazy('profile_list')
    permissions = AdministratorPermissions()

    def get_initial(self):
        initial = self.initial.copy()
        user_dict = self.object.__dict__.copy()
        user_dict.pop('password')
        user_dict.pop('email')
        initial.update(user_dict)
        return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        user_dict = form.cleaned_data.copy()
        if not user_dict['password1']:
            user_dict.pop('password1')
        if not user_dict['password2']:
            user_dict.pop('password2')
        if not user_dict['email']:
            user_dict.pop('email')
        self.object.__dict__.update(user_dict)
        self.object.save()
        messages.success(self.request, 'Profile "%s" updated successfully!' % self.object.full_name)
        return HttpResponseRedirect(self.get_success_url())


class ProfileDeleteView(PermissionsDeleteView):

    model = Profile
    template_name = 'delete.html'
    success_url = reverse_lazy('profile_list')
    permissions = AdministratorPermissions()

    def post(self, *args, **kwargs):
        if 'cancel' in self.request.POST:
            return HttpResponseRedirect(reverse('profile_list'))
        else:
            messages.success(self.request, 'Profile deleted successfully!')
            return self.delete(*args, **kwargs)


class AuthorDetailView(PermissionsDetailView):

    model = Profile
    permissions = UserPermissions()


class ProfileSettingsUpdateView(PermissionsUpdateView):

    model = Profile
    success_url = reverse_lazy('profile_settings')
    form_class = ProfileUpdateForm
    template_name = 'profiles/profile_settings.html'
    permissions = UserPermissions()

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Your settings were successfully updated!')
        return super(ProfileSettingsUpdateView, self).form_valid(form)


class AvatarChangeView(PermissionsTemplateView):

    template_name = 'avatar/change.html'
    permissions = UserPermissions()

    def get_context_data(self, **kwargs):
        context = super(AvatarChangeView, self).get_context_data(**kwargs)
        avatar, avatars = _get_avatars(self.request.user)
        if avatar:
            avatar_kwargs = {'initial': {'choice': avatar.id}}
        else:
            avatar_kwargs = {}
        upload_avatar_form = UploadAvatarForm(None, None, user=self.request.user)
        primary_avatar_form = PrimaryAvatarForm(None, user=self.request.user, avatars=avatars, **avatar_kwargs)

        context.update({
            'avatar': avatar,
            'avatars': avatars,
            'upload_avatar_form': upload_avatar_form,
            'primary_avatar_form': primary_avatar_form,
        })
        return context

    def post(self, *args, **kwargs):
        avatar, avatars = _get_avatars(self.request.user)
        if 'add' in self.request.POST and 'avatar' in self.request.FILES:
            upload_avatar_form = UploadAvatarForm(self.request.POST, self.request.FILES, user=self.request.user)
            if upload_avatar_form.is_valid():
                avatar = Avatar(user=self.request.user, primary=True)
                image_file = self.request.FILES['avatar']
                avatar.avatar.save(image_file.name, image_file)
                avatar.save()
                messages.success(self.request, 'Successfully uploaded a new avatar.')
                avatar_updated.send(sender=Avatar, user=self.request.user, avatar=avatar)
            return HttpResponseRedirect(reverse('avatar_change'))
        elif 'change' in self.request.POST:
            primary_avatar_form = PrimaryAvatarForm(self.request.POST, user=self.request.user, avatars=avatars)
            if 'choice' in self.request.POST and primary_avatar_form.is_valid():
                avatar = Avatar.objects.get(id=primary_avatar_form.cleaned_data['choice'])
                avatar.primary = True
                avatar.save()
                avatar_updated.send(sender=Avatar, user=self.request.user, avatar=avatar)
                messages.success(self.request, 'Successfully updated your avatar.')
            return HttpResponseRedirect(reverse('avatar_change'))
        elif 'delete' in self.request.POST:
            delete_avatar_form = PrimaryAvatarForm(self.request.POST, user=self.request.user, avatars=avatars)
            if delete_avatar_form.is_valid():
                ids = delete_avatar_form.cleaned_data['choice']
                if six.text_type(avatar.id) in ids and avatars.count() > len(ids):
                    for a in avatars:
                        if six.text_type(a.id) not in ids:
                            a.primary = True
                            a.save()
                            avatar_updated.send(sender=Avatar, user=self.request.user, avatar=avatar)
                            break
                Avatar.objects.filter(id__in=ids).delete()
                messages.success(self.request, 'Selected avatar successfully deleted.')
            return HttpResponseRedirect(reverse('avatar_change'))
        return HttpResponseRedirect(reverse('avatar_change'))
