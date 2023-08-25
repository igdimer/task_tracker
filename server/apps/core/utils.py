import hashlib

from django.conf import settings


def hash_password(password: str, email: str) -> str:
    """Hash user password to save into database."""
    secret = settings.AUTH_SECRET
    string = secret + password + email
    hashed_password = hashlib.sha256(string.encode())

    return hashed_password.hexdigest()
