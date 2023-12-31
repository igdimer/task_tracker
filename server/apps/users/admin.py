from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """User representation on admin site."""

    list_display = ('email', 'first_name', 'last_name', 'created_at', 'updated_at')
    search_fields = ('email', )
    fields = ('id', 'email', 'first_name', 'last_name', 'is_admin', ('created_at', 'updated_at'))
    readonly_fields = ('id', 'created_at', 'updated_at')
