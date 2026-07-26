from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView
from legal_information_assistance_system.users.views import password_reset_confirm_view
from legal_information_assistance_system.users.views import password_reset_done_view
from legal_information_assistance_system.legal_ai.admin import analytics_dashboard_view
from legal_information_assistance_system.legal_ai.admin import ingestion_dashboard_view
from legal_information_assistance_system.legal_ai.admin import mark_all_notifications_read
from legal_information_assistance_system.legal_ai.admin import retrieval_debugger_view
from legal_information_assistance_system.legal_ai.api.views import (
    ConversationDetailView,
    ConversationListCreateView,
)

urlpatterns = [
    path("reset-password/", password_reset_confirm_view, name="password-reset-confirm"),
    path("reset-password/done/", password_reset_done_view, name="password-reset-done"),
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    path("users/", include("legal_information_assistance_system.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    path("admin/legal-ai/ingestion/", ingestion_dashboard_view, name="ingestion_dashboard"),
    path("admin/legal-ai/analytics/", analytics_dashboard_view, name="analytics_dashboard"),
    path("admin/legal-ai/retrieval-debugger/", retrieval_debugger_view, name="retrieval_debugger"),
    path("admin/legal_ai/mark-all-read/", mark_all_notifications_read, name="mark_all_notifications_read"),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

urlpatterns += [
    path("api/auth/", include("legal_information_assistance_system.users.api.urls")),
    path("api/", include("config.api_router")),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    path("api/legal-ai/", include("legal_information_assistance_system.legal_ai.api.urls")),
    # Direct routes for frontend compatibility
    path("api/conversations/", ConversationListCreateView.as_view(), name="conversations"),
    path("api/conversations/<int:pk>/", ConversationDetailView.as_view(), name="conversation-detail"),
    path(
        "api/",
        include("legal_information_assistance_system.users.api.urls"),
    ),
]

if settings.DEBUG:
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            *urlpatterns,
        ]
