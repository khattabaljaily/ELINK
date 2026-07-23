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
