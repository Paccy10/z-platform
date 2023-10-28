import jwt
from rest_framework import generics, mixins, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.urls import reverse
from django.template.loader import get_template
from django_rq import enqueue

from apps.users.models import User
from apps.users.serializers import UserSerializer, LoginSerializer
from apps.users.constants.messages.error import errors
from apps.common.utils import send_email
from core.settings.base import env


class UserSignupView(mixins.CreateModelMixin, generics.GenericAPIView):
    """User signup view"""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        response = self.create(request, *args, **kwargs)

        # Send verification email
        user = User.objects.get(id=response.data["id"])
        token = RefreshToken.for_user(user).access_token
        current_path = reverse("confirm")
        url = (
            f"{request.scheme}://{request.get_host()}{current_path}?token={str(token)}"
        )
        subject = "Email Confirmation"
        message = get_template("confirmation.html").render({"user": user, "url": url})
        enqueue(send_email, subject, message, [user.email])

        return response


class UserConfirmationView(generics.GenericAPIView):
    """User confirmation view"""

    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, env("SECRET_KEY"), algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])

            if not user.is_active:
                user.is_active = True
                user.save()

            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response(
                {"token": [errors["token"]["expired"]]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.DecodeError:
            return Response(
                {"token": [errors["token"]["invalid"]]},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserLoginView(generics.GenericAPIView):
    """User login view"""

    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
