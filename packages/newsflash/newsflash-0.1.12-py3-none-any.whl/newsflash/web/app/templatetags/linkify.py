import re
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe


register = template.Library()

URL_PATTERN = re.compile(r"\[([^\]]+)\]\((https://[^\s)]+)\)")


@register.filter(name="linkify")
@stringfilter
def linkify(value: str) -> str:
    def replace_url(match):
        text = match.group(1)
        url = match.group(2)
        return f'<a href="{url}" target="_blank">{text}</a>'

    result = URL_PATTERN.sub(replace_url, value)
    return mark_safe(result)
