
from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import User, LawyerProfile
from django.contrib import admin


if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    model = User

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
        "is_verified",
    )

    search_fields = (
        "email",
        "username",
        "first_name",
        "last_name",
    )

    ordering = ("email",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "username",
                    "password",
                ),
            },
        ),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                ),
            },
        ),
        (
            _("Verification"),
            {
                "fields": (
                    "is_verified",
                ),
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important dates"),
            {
                "fields": (
                    "last_login",
                    "date_joined",
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):

    list_display = (
        "full_name",
        "specialization",
        "city",
        "years_of_experience",
    )

    search_fields = (
        "full_name",
        "specialization",
        "city",
    )

    list_filter = (
        "specialization",
        "city",
    )    