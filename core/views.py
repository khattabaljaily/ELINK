from django.shortcuts import render
from django.urls import reverse


def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse('sitemap'))
    return render(request, 'robots.txt', {'sitemap_url': sitemap_url}, content_type='text/plain')
