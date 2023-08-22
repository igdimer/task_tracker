from django.contrib import admin

from .models import Comment, Issue, Project, Release


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Project representation on admin site."""

    list_display = ('id', 'title', 'code')
    fields = ('id', 'title', 'code', 'description')
    readonly_fields = ('id',)


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Release representation on admin site."""

    list_display = ('id', 'project', 'version', 'release_date', 'status')
    fields = ('id', 'project', 'version', 'release_date', 'status')
    readonly_fields = ('id',)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Issue representation on admin site."""

    list_display = ('project', 'title', 'status', 'author', 'assignee')
    readonly_fields = ('code', 'id')
    fields = (
        'id',
        'title',
        'code',
        'description',
        'estimated_time',
        'logged_time',
        'status',
        'author',
        'assignee',
        'project',
        'release',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Comment representation on admin site."""

    list_display = ('issue', 'author')
