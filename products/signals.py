from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import ProductImage


@receiver(post_delete, sender=ProductImage)
def delete_image_file(sender, instance, **kwargs):
    """Remove the image file from storage once its row is gone.

    Fires for direct ProductImage deletion and for the cascade delete
    that runs when a Product is deleted, so no orphaned files are left
    behind in media/products/ either way.
    """
    if instance.image:
        instance.image.delete(save=False)
