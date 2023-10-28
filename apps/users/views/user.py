from datetime import date
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.profiles.models import Profile
from apps.profiles.serializers import EditProfileSerializer, ProfileDisplaySerializer


class MyProfileView(generics.GenericAPIView):
    """User own profile view"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        data = ProfileDisplaySerializer(profile, context={"request": request}).data

        return Response(data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = EditProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user_data = {k: data.get(k) for k in ["firstname", "lastname", "middlename"]}
        profile_data = {
            k: data.get(k)
            for k in [
                "photo",
                "gender",
                "date_of_birth",
                "marital_status",
                "nationality",
            ]
        }

        # Calculating age
        today = date.today()
        date_of_birth = data.get("date_of_birth")
        profile_data["age"] = (
            today.year
            - date_of_birth.year
            - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        )
        profile = Profile.objects.get(user=request.user)

        for attr, value in user_data.items():
            setattr(profile.user, attr, value)
        profile.user.save()

        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return Response(
            ProfileDisplaySerializer(profile, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )
