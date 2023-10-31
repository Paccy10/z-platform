import pytest
from rest_framework.test import APIClient

from apps.users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def base_user(db):
    new_user = User.objects.create(
        firstname="new", lastname="user", email="new.user@app.com", password="password"
    )
    return new_user
