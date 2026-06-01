from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import UpdateView

from legal_information_assistance_system.users.forms import PasswordResetConfirmForm
from legal_information_assistance_system.users.models import User
from legal_information_assistance_system.users.services import reset_user_password

if TYPE_CHECKING:
    from django.db.models import QuerySet


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["first_name", "last_name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None = None) -> User:
        assert self.request.user.is_authenticated
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()


class PasswordResetConfirmView(View):
    """Web page linked from password-reset emails (no separate frontend required)."""

    template_name = "users/password_reset_confirm.html"

    def _get_uid_token(self, request, *, from_post: bool = False):
        source = request.POST if from_post else request.GET
        uid = (source.get("uid") or "").strip()
        token = (source.get("token") or "").strip()
        # Some clients break query strings; normalize common encoding mistakes.
        token = token.replace("&amp;", "").split("&")[0]
        return uid, token

    def get(self, request):
        uid, token = self._get_uid_token(request)
        if not uid or not token:
            return render(request, self.template_name, {"invalid_link": True})

        return render(
            request,
            self.template_name,
            {
                "form": PasswordResetConfirmForm(),
                "uid": uid,
                "token": token,
            },
        )

    def post(self, request):
        uid, token = self._get_uid_token(request, from_post=True)
        form = PasswordResetConfirmForm(request.POST)

        if not uid or not token:
            return render(request, self.template_name, {"invalid_link": True})

        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {"form": form, "uid": uid, "token": token},
            )

        try:
            reset_user_password(
                uid=uid,
                token=token,
                new_password=form.cleaned_data["new_password"],
            )
        except ValidationError as exc:
            messages.error(request, " ".join(exc.messages))
            return render(
                request,
                self.template_name,
                {"form": form, "uid": uid, "token": token},
            )

        messages.success(
            request,
            _("Your password has been reset. You can now log in with your new password."),
        )
        return redirect("password-reset-done")


password_reset_confirm_view = PasswordResetConfirmView.as_view()


def password_reset_done_view(request):
    return render(request, "users/password_reset_done.html")
