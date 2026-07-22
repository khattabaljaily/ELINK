from django.shortcuts import render

from .models import SiteSettings

ALLOWED_PREFIXES = ('/dashboard/', '/admin/', '/accounts/', '/static/', '/media/')


class ComingSoonMiddleware:
    """Shows a coming soon page to visitors while maintenance_mode is on.

    Staff always pass through, and the dashboard/admin/accounts paths stay
    reachable so staff can log in and switch the mode back off.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(ALLOWED_PREFIXES):
            return self.get_response(request)

        if request.user.is_authenticated and request.user.is_staff:
            return self.get_response(request)

        settings = SiteSettings.load()
        if settings.maintenance_mode:
            return render(request, 'coming_soon.html', {'message': settings.coming_soon_message}, status=503)

        return self.get_response(request)
