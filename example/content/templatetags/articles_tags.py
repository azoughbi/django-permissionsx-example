from django import template

from classytags.core import Options
from classytags.arguments import Argument
from classytags.helpers import AsTag

from example.content.models import Topic


register = template.Library()


@register.filter
def obj_type_name(obj):
    return type(obj).__name__


class GetTopics(AsTag):
    options = Options(
        'as',
        Argument('varname', resolve=False, required=True),
    )

    def get_value(self, context):
        return Topic.objects.filter(level=0)


register.tag(GetTopics)
