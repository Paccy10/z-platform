from datetime import date
from rest_framework import generics, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.template.loader import get_template
from django_rq import enqueue

from apps.profiles.models import Profile, AccountVerification
from apps.profiles.serializers import (
    EditProfileSerializer,
    ProfileDisplaySerializer,
    VerificationRequestSerializer,
    VerificationRequestDisplaySerializer,
    VerificationRequestReviewSerializer,
)
from apps.profiles.constants.messages.error import (
    REQUEST_NOT_FOUND,
    REQUEST_ALREADY_REVIEWED,
)
from apps.profiles.constants.status import (
    RequestAnswer,
    RequestStatus,
    VerificationStatus,
)
from apps.common.utils import send_email


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


class VerificationRequestView(mixins.CreateModelMixin, generics.GenericAPIView):
    """User verification request view"""

    queryset = AccountVerification.objects.all()
    serializer_class = VerificationRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class VerificationRequestsView(mixins.ListModelMixin, generics.GenericAPIView):
    """User verification requests view"""

    queryset = AccountVerification.objects.prefetch_related("user").all()
    serializer_class = VerificationRequestDisplaySerializer
    permission_classes = [IsAuthenticated]
    search_fields = [
        "id_document_number",
        "user__firstname",
        "user__lastname",
        "user__middlename",
        "user__email",
    ]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class VerificationRequestDetailsView(
    mixins.RetrieveModelMixin, generics.GenericAPIView
):
    """User verification request details view"""

    queryset = AccountVerification.objects.all()
    serializer_class = VerificationRequestDisplaySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class VerificationRequestReviewView(generics.GenericAPIView):
    """User verification request review view"""

    serializer_class = VerificationRequestReviewSerializer

    def post(self, request, id):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        verification_request = AccountVerification.objects.filter(id=id).first()

        if not verification_request:
            raise NotFound(REQUEST_NOT_FOUND)

        if verification_request.status != RequestStatus.PENDING.value:
            return Response(
                {"detail": REQUEST_ALREADY_REVIEWED}, status=status.HTTP_400_BAD_REQUEST
            )

        answer = serializer.validated_data.get("answer")
        profile = verification_request.user.profile

        if answer == RequestAnswer.APPROVE.value:
            verification_request.status = RequestStatus.APPROVED.value
            profile.status = VerificationStatus.VERIFIED.value
        else:
            verification_request.status = RequestStatus.REJECTED.value
            profile.status = VerificationStatus.UNVERIFIED.value

        verification_request.save()
        profile.save()

        subject = "Verification Request Status"
        message = get_template("verification.html").render(
            {"user": verification_request.user, "status": verification_request.status}
        )
        enqueue(send_email, subject, message, [verification_request.user.email])

        return Response(
            VerificationRequestDisplaySerializer(
                verification_request, context={"request": request}
            ).data,
            status=status.HTTP_200_OK,
        )
