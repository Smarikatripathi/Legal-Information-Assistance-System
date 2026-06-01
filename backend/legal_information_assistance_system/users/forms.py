from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.utils.translation import gettext_lazy as _

from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm

User = get_user_model()


class UserAdminChangeForm(DjangoUserChangeForm):
    class Meta(DjangoUserChangeForm.Meta):
        model = User


class UserAdminCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ("email", "username")


class UserSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        return user


class UserSocialSignupForm(SocialSignupForm):
    pass


class PasswordResetConfirmForm(forms.Form):
    new_password = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
        min_length=8,
    )
    confirm_password = forms.CharField(
        label=_("Confirm new password"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError(_("Passwords do not match."))
        return cleaned_data
