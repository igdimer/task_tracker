from rest_framework import serializers


def _create_serializer_class(name, fields) -> type[serializers.Serializer]:
    return type(name, (serializers.Serializer, ), fields)


def inline_serializer(*, fields, data=None, **kwargs) -> serializers.Serializer:
    """Create serializer dynamically."""
    serializer_class = _create_serializer_class(name='', fields=fields)

    if data is not None:
        return serializer_class(data=data, **kwargs)

    return serializer_class(**kwargs)
