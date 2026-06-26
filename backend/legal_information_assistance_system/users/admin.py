# from allauth.account.decorators import secure_admin_login
# from django.conf import settings
# from django.contrib import admin
# from django.contrib.auth import admin as auth_admin
# from django.utils.translation import gettext_lazy as _

# from .forms import UserAdminChangeForm
# from .forms import UserAdminCreationForm
# from .models import User

# if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
#     # Force the `admin` sign in process to go through the `django-allauth` workflow:
#     # https://docs.allauth.org/en/latest/common/admin.html#admin
#     admin.autodiscover()
#     admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


# @admin.register(User)
# class UserAdmin(auth_admin.UserAdmin):
#     form = UserAdminChangeForm
#     add_form = UserAdminCreationForm

#     fieldsets = (
#         (None, {"fields": ("username", "password")}),
#         (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
#         (
#             _("Permissions"),
#             {
#                 "fields": (
#                     "is_active",
#                     "is_staff",
#                     "is_superuser",
#                     "groups",
#                     "user_permissions",
#                 ),
#             },
#         ),
#         (_("Important dates"), {"fields": ("last_login", "date_joined")}),
#     )

#     list_display = ["username", "email", "is_superuser"]

#     search_fields = ["username", "email"]

from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import User

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