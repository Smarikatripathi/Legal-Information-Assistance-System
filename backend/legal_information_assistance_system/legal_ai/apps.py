from django.apps import AppConfig


class LegalAiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "legal_information_assistance_system.legal_ai"

    def ready(self):
        """
        Register custom Legal AI admin URLs.

        The main admin dashboard and other custom admin pages
        are handled inside legal_ai.admin.

        This file registers the Retrieval Debugger URL.
        """

        from django.contrib import admin
        from django.urls import path

        from legal_information_assistance_system.legal_ai.admin import (
            retrieval_debugger_view,
        )

        # Prevent duplicate URL registration during
        # Django's development autoreloader.
        if getattr(
            admin.site,
            "_legal_ai_urls_registered",
            False,
        ):
            return

        original_get_urls = admin.site.get_urls

        def get_urls_with_legal_ai():
            custom_urls = [
                path(
                    "legal_ai/retrieval-debugger/",
                    admin.site.admin_view(
                        retrieval_debugger_view
                    ),
                    name="retrieval-debugger",
                ),
            ]

            return custom_urls + original_get_urls()

        admin.site.get_urls = get_urls_with_legal_ai

        admin.site._legal_ai_urls_registered = True

