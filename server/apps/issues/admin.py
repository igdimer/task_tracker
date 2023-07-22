from django.contrib import admin

from .models import Comment, Issue, Project, Release


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Project representation on admin site."""

    list_display = ('title', 'code')


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Release representation on admin site."""

    list_display = ('project', 'version', 'release_date', 'status')


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Issue representation on admin site."""

    list_display = ('project', 'title', 'status', 'author', 'assignee')
    readonly_fields = ('code', )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Comment representation on admin site."""

    list_display = ('issue', 'author')
