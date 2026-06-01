from django.urls import path

from legal_information_assistance_system.users.api.urls import auth_urlpatterns
from legal_information_assistance_system.users.views import user_detail_view
from legal_information_assistance_system.users.views import user_redirect_view
from legal_information_assistance_system.users.views import user_update_view

app_name = "users"

urlpatterns = [
    *auth_urlpatterns,
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<str:username>/", view=user_detail_view, name="detail"),
]
