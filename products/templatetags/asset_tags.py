import os

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def static_versioned(path):
    """Like {% static %}, but appends the file's mtime as a cache-busting
    query string in DEBUG so edits show up on a normal refresh."""
    url = static(path)
    if settings.DEBUG:
        abs_path = finders.find(path)
        if abs_path:
            url = f"{url}?v={int(os.path.getmtime(abs_path))}"
    return url
