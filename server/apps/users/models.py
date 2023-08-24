from django.db import models

from server.apps.core.models import BaseModel


class User(BaseModel):
    """User model."""

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    password = models.CharField(max_length=64)
    is_admin = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        """Text representation."""
        return f'{self.first_name} {self.last_name}'
