from __future__ import annotations

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework_simplejwt.tokens import RefreshToken

from legal_information_assistance_system.users.email import send_password_reset_email

User = get_user_model()


def get_tokens_for_user(user: User) -> dict[str, str]:
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def authenticate_user(*, email: str, password: str) -> User | None:
    return authenticate(username=email, password=password)


def blacklist_refresh_token(refresh_token: str) -> None:
    token = RefreshToken(refresh_token)
    token.blacklist()


def change_user_password(*, user: User, old_password: str, new_password: str) -> None:
    if not user.check_password(old_password):
        raise ValidationError("Current password is incorrect.", code="invalid_password")

    validate_password(new_password, user=user)
    user.set_password(new_password)
    user.save(update_fields=["password"])


def build_password_reset_link(*, user: User, frontend_base_url: str) -> str:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    base = frontend_base_url.rstrip("/")
    return f"{base}/reset-password?uid={uid}&token={token}"


def request_password_reset(*, email: str, frontend_base_url: str) -> None:
    user = User.objects.filter(email__iexact=email).first()
    if user is None or not user.is_active:
        return

    reset_link = build_password_reset_link(user=user, frontend_base_url=frontend_base_url)
    send_password_reset_email(user=user, reset_link=reset_link)


def reset_user_password(*, uid: str, token: str, new_password: str) -> User:
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as exc:
        raise ValidationError("Invalid or expired reset link.", code="invalid_token") from exc

    if not default_token_generator.check_token(user, token):
        raise ValidationError("Invalid or expired reset link.", code="invalid_token")

    validate_password(new_password, user=user)
    user.set_password(new_password)
    user.save(update_fields=["password"])
    return user
