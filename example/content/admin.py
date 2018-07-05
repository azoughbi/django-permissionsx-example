from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from example.content.models import (
    Article,
    Comment,
    Topic,
)


admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(Topic, MPTTModelAdmin)
