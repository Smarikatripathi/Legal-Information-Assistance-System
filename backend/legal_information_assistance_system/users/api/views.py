from __future__ import annotations

import requests
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
   
)

from .serializers import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    ProfileUpdateSerializer,
  
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


class GoogleOAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response(
                {"detail": "Authorization code is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if Google OAuth is configured
        try:
            social_providers = settings.SOCIALACCOUNT_PROVIDERS
            google_config = social_providers.get("google", {})
            app_config = google_config.get("APP", {})
            client_id = app_config.get("client_id")
            client_secret = app_config.get("secret")
            
            if not client_id or not client_secret:
                return Response(
                    {"detail": "Google OAuth is not configured. Please set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_SECRET in environment variables."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        except Exception as e:
            return Response(
                {"detail": f"Google OAuth configuration error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Exchange authorization code for access token
        try:
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
            redirect_uri = f"{frontend_url}/auth/callback/google/"
            
            token_response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                }
            )
            token_response.raise_for_status()
            token_data = token_response.json()
            access_token = token_data.get("access_token")
        except requests.RequestException as e:
            return Response(
                {"detail": f"Failed to exchange authorization code for access token: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get user info from Google
        try:
            user_info_response = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_info_response.raise_for_status()
            user_info = user_info_response.json()
        except requests.RequestException as e:
            return Response(
                {"detail": f"Failed to get user info from Google: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = user_info.get("email")
        if not email:
            return Response(
                {"detail": "Email not found in Google user info."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create new user with Google info
            username = email.split("@")[0]
            # Ensure username is unique
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User.objects.create_user(
                email=email,
                username=username,
                password=None,  # No password for OAuth users
            )

        return Response(get_tokens_for_user(user))



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