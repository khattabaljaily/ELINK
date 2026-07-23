from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STAFF = 'staff', 'Staff'
        MANAGER = 'manager', 'Manager'

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=32, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STAFF)

    last_seen_at = models.DateTimeField(null=True, blank=True)
    last_seen_ip = models.GenericIPAddressField(null=True, blank=True)
    last_seen_location = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_manager(self):
        return self.is_superuser or self.role == self.Role.MANAGER
