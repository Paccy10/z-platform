import pytest
import json
import datetime
from django.urls import reverse
from time import sleep

from tests.constants import JSON_CONTENT_TYPE
from apps.users.constants.messages.error import errors
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
class TestUserSignupEndpoint:
    """Test user signup endpoint"""

    url = reverse("signup")
    data = {
        "firstname": "Test",
        "lastname": "USer",
        "email": "test.user@app.com",
        "password": "Password@1234",
    }

    def test_user_signup_succeeds(self, api_client, mocker):
        mocker.patch("django_rq.enqueue")

        data = self.data.copy()
        data = json.dumps(data)
        response = api_client.post(self.url, data=data, content_type=JSON_CONTENT_TYPE)

        assert response.status_code == 201
        assert response.json()["email"] == self.data["email"]
        assert response.json()["is_active"] is False

    def test_user_signup_without_firstname_fails(self, api_client):
        data = self.data.copy()
        data.pop("firstname")
        data = json.dumps(data)
        response = api_client.post(self.url, data=data, content_type=JSON_CONTENT_TYPE)

        assert response.status_code == 400
        assert response.json()["firstname"] == [errors["firstname"]["required"]]

    def test_user_signup_with_blank_firstname_fails(self, api_client):
        data = self.data.copy()
        data["firstname"] = ""
        data = json.dumps(data)
        response = api_client.post(self.url, data=data, content_type=JSON_CONTENT_TYPE)

        assert response.status_code == 400
        assert response.json()["firstname"] == [errors["firstname"]["blank"]]

    def test_user_signup_without_lastname_fails(self, api_client):
        data = self.data.copy()
        data.pop("lastname")
        data = json.dumps(data)
        response = api_client.post(self.url, data=data, content_type=JSON_CONTENT_TYPE)

        assert response.status_code == 400
        assert response.json()["lastname"] == [errors["lastname"]["required"]]

    def test_user_signup_with_blank_lastname_fails(self, api_client):
        data = self.data.copy()
        data["lastname"] = ""
        data = json.dumps(data)
        response = api_client.post(self.url, data=data, content_type=JSON_CONTENT_TYPE)

        assert response.status_code == 400
        assert response.json()["lastname"] == [errors["lastname"]["blank"]]

    def test_user_signup_without_email_fails(self, api_client):
        data = self.data.copy()
        data.pop("email")
        data = json.dumps(data)
        response = api_client.post(self.url, data=data, content_type=JSON_CONTENT_TYPE)

        assert response.status_code == 400
        assert response.json()["email"] == [errors["email"]["required"]]

    def test_user_signup_with_blank_email_fails(self, api_client):
        data = self.data.copy()
        data["email"] = ""
        data = json.dumps(data)
        response = api_client.post(self.url, data=data, content_type=JSON_CONTENT_TYPE)

        assert response.status_code == 400
        assert response.json()["email"] == [errors["email"]["blank"]]

    def test_user_signup_with_taken_email_fails(self, api_client, base_user):
        data = self.data.copy()
        data["email"] = base_user.email
        data = json.dumps(data)
        response = api_client.post(self.url, data=data, content_type=JSON_CONTENT_TYPE)

        assert response.status_code == 409
        assert response.json()["detail"] == errors["email"]["unique"]

    def test_user_signup_without_password_fails(self, api_client):
        data = self.data.copy()
        data.pop("password")
        data = json.dumps(data)
        response = api_client.post(self.url, data=data, content_type=JSON_CONTENT_TYPE)

        assert response.status_code == 400
        assert response.json()["password"] == [errors["password"]["required"]]

    def test_user_signup_with_blank_password_fails(self, api_client):
        data = self.data.copy()
        data["password"] = ""
        data = json.dumps(data)
        response = api_client.post(self.url, data=data, content_type=JSON_CONTENT_TYPE)

        assert response.status_code == 400
        assert response.json()["password"] == [errors["password"]["blank"]]

    def test_user_signup_with_weak_password_fails(self, api_client):
        data = self.data.copy()
        data["password"] = "hello"
        data = json.dumps(data)
        response = api_client.post(self.url, data=data, content_type=JSON_CONTENT_TYPE)

        assert response.status_code == 400
        assert response.json()["password"] == [
            errors["password"]["weak"],
            errors["password"]["min_length"],
        ]


@pytest.mark.django_db
class TestUserConfirmationEndpoint:
    """Test user confirmation endpoint"""

    url = reverse("confirm")

    def test_user_confirmation_succeeds(self, api_client, base_user):
        token = RefreshToken.for_user(base_user).access_token
        response = api_client.get(
            f"{self.url}?token={str(token)}", content_type=JSON_CONTENT_TYPE
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is True

    def test_user_confirmation_with_invalid_token_fails(self, api_client, base_user):
        response = api_client.get(
            f"{self.url}?token=token", content_type=JSON_CONTENT_TYPE
        )

        assert response.status_code == 400
        assert response.json()["token"] == [errors["token"]["invalid"]]

    def test_user_confirmation_with_expired_token_fails(self, api_client, base_user):
        token = RefreshToken.for_user(base_user).access_token
        token.set_exp(lifetime=datetime.timedelta(seconds=1))
        sleep(2)
        response = api_client.get(
            f"{self.url}?token={str(token)}", content_type=JSON_CONTENT_TYPE
        )

        assert response.status_code == 400
        assert response.json()["token"] == [errors["token"]["expired"]]
