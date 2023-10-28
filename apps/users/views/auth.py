from rest_framework import generics, mixins

from apps.users.models import User
from apps.users.serializers import UserSerializer


class UserSignupView(mixins.CreateModelMixin, generics.GenericAPIView):
    """User signup view"""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
