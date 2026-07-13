from django.apps import AppConfig


class LegalAiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "legal_information_assistance_system.legal_ai"

    def ready(self):
        # Register custom admin URLs once
        from django.contrib import admin
        from django.urls import path

        from legal_information_assistance_system.legal_ai.admin import (
            analytics_dashboard_view,
            ingestion_dashboard_view,
            retrieval_debugger_view,
        )

        if getattr(admin.site, "_legal_ai_urls_registered", False):
            return

        original_get_urls = admin.site.get_urls

        def get_urls_with_legal_ai():
            custom = [
                path(
                    "legal-ai/retrieval-debugger/",
                    admin.site.admin_view(retrieval_debugger_view),
                    name="retrieval-debugger",
                ),
                path(
                    "legal-ai/ingestion/",
                    admin.site.admin_view(ingestion_dashboard_view),
                    name="ingestion-dashboard",
                ),
                path(
                    "legal-ai/analytics/",
                    admin.site.admin_view(analytics_dashboard_view),
                    name="rag-analytics",
                ),
            ]
            return custom + original_get_urls()

        admin.site.get_urls = get_urls_with_legal_ai
        admin.site._legal_ai_urls_registered = True
