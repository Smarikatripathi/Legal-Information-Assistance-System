from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenRefreshView

from legal_information_assistance_system.users.models import User
from legal_information_assistance_system.users.services import (
    authenticate_user,
    blacklist_refresh_token,
    change_user_password,
    get_tokens_for_user,
    request_password_reset,
    reset_user_password,
)

from .serializers import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    ProfileUpdateSerializer,
    ResetPasswordSerializer,
    SignupSerializer,
    UserSerializer,
)
from rest_framework import generics
from ..models import LawyerProfile
from .serializers import LawyerProfileSerializer

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(get_tokens_for_user(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(get_tokens_for_user(user))


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            blacklist_refresh_token(serializer.validated_data["refresh"])
        except Exception:
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Logged out successfully."})


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            change_user_password(
                user=request.user,
                old_password=serializer.validated_data["old_password"],
                new_password=serializer.validated_data["new_password"],
            )
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Password changed successfully."})


class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user, context={"request": request}).data)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_password_reset(
            email=serializer.validated_data["email"],
            frontend_base_url=settings.PASSWORD_RESET_BASE_URL,
        )
        return Response(
            {
                "detail": (
                    "If an account exists with this email, "
                    "password reset instructions have been sent."
                ),
            },
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            reset_user_password(
                uid=serializer.validated_data["uid"],
                token=serializer.validated_data["token"],
                new_password=serializer.validated_data["new_password"],
            )
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Password reset successful."})


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.get_serializer(request.user).data)


class TokenRefreshAPIView(TokenRefreshView):
    permission_classes = [AllowAny]

class LawyerListAPIView(generics.ListAPIView):
    """
    Returns all lawyer profiles.
    """

    serializer_class = LawyerProfileSerializer
    permission_classes = [AllowAny]

    queryset = LawyerProfile.objects.all().order_by("full_name")


class LawyerDetailAPIView(generics.RetrieveAPIView):
    """
    Returns a single lawyer profile.
    """

    serializer_class = LawyerProfileSerializer
    permission_classes = [AllowAny]

    queryset = LawyerProfile.objects.all()