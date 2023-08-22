from rest_framework import serializers


class IssueOutputSerializer(serializers.Serializer):
    """Serializer for full output of issue."""

    title = serializers.CharField()
    code = serializers.CharField()
    description = serializers.CharField()
    estimated_time = serializers.DurationField()
    logged_time = serializers.DurationField()
    remaining_time = serializers.DurationField()
    author = serializers.IntegerField(source='author_id')
    assignee = serializers.IntegerField(source='assignee_id')
    project = serializers.CharField(source='project.code')
    status = serializers.CharField()
    release = serializers.CharField(source='get_release_version')
