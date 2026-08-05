from django.conf import settings
from django.db import models


class SiteSettings(models.Model):
    """Singleton row holding site-wide toggles controlled from the dashboard."""

    maintenance_mode = models.BooleanField(default=False)
    coming_soon_message = models.TextField(
        blank=True,
        default="We're putting the finishing touches on something great. Check back soon.",
    )
    ads_enabled = models.BooleanField(
        default=True,
        help_text='Show advertising banners on the homepage, cart, and checkout pages.',
    )

    class Meta:
        verbose_name = 'Site settings'
        verbose_name_plural = 'Site settings'

    def __str__(self):
        return 'Site settings'

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class VisitLog(models.Model):
    """One row per real page view, for the admin visitor-analytics report.

    Deliberately cookie-free: anonymous visitors are identified by a hash of
    IP + user agent salted with the current date, so nothing here is
    reversible to an IP and nothing can be correlated across days."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    location = models.CharField(max_length=100, blank=True)
    visitor_hash = models.CharField(max_length=64, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='visit_logs',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.created_at:%Y-%m-%d %H:%M} — {self.location or "Unknown"}'
