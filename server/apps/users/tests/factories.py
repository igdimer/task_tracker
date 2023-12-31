import factory

from ..models import User


class UserFactory(factory.django.DjangoModelFactory):
    """User factory."""

    class Meta:
        model = User
        django_get_or_create = ('email',)

    email = 'test@email.com'
    first_name = 'Ozzy'
    last_name = 'Osbourne'
    password = 'fake_hashed_password'  # noqa: S105
