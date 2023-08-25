from getpass import getpass

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.validators import validate_email

from server.apps.users.services import UserService


class Command(BaseCommand):
    """The command for creation admin user."""

    help = 'Create admin user'

    def handle(self, *args, **options):
        """Command execution."""
        self.stdout.write('Create admin user')

        while True:
            email = input('Type email: ')
            try:
                validate_email(email)
            except ValidationError:
                self.stdout.write('Wrong email format')
                continue

            try:
                UserService.get_by_email(email)
            except UserService.UserNotFoundError:
                break
            else:
                self.stdout.write('User with this email already exists.')
                continue

        first_name = input('Type first name: ')
        last_name = input('Type last name: ')

        while True:
            password_1 = getpass('Type password: ')
            password_2 = getpass('Repeat password: ')
            if password_1 != password_2:
                self.stdout.write('Typed passwords are not equal')
                continue
            else:
                break

        UserService.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password_1,
            is_admin=True,
        )

        self.stdout.write('Admin user was successfully created.')
