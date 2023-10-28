from rest_framework import status
from rest_framework.exceptions import APIException
from django.core.mail import EmailMessage


class ConflictException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Conflict error"

    def __init__(self, detail=None):
        super().__init__(detail=detail)


def validate_unique_value(**kwargs):
    field = kwargs["field"]
    value = kwargs["value"]
    errors = kwargs["errors"]
    model = kwargs["model"]
    instance = kwargs["instance"]
    query = {field: value}

    row = model.objects.filter(**query).first()

    if row and not instance:
        raise ConflictException(errors[field]["unique"])


def send_email(subject, message, to):
    email_message = EmailMessage(subject, message, to=to)
    email_message.content_subtype = "html"
    email_message.send()
