from django import forms

from tinymce.widgets import TinyMCE

from example.content.models import (
    Article,
)


class ArticleAuthorAddEditForm(forms.ModelForm):

    content = forms.CharField(widget=TinyMCE())

    class Meta:
        model = Article
        fields = ('topic', 'title', 'lead', 'content', 'is_pending')


class ArticlePublisherAddEditForm(forms.ModelForm):

    content = forms.CharField(widget=TinyMCE())

    class Meta:
        model = Article
        fields = ('topic', 'title', 'lead', 'content', 'is_published')
