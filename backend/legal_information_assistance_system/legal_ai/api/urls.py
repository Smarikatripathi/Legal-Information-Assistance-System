from django.urls import path

from legal_information_assistance_system.legal_ai.api.views import (
    ConversationDetailView,
    ConversationListCreateView,
    CrawlLawCommissionView,
    DocumentListView,
    LegalQueryView,
    QueryHistoryListView,
    UploadPDFView,
)

urlpatterns = [
    path("upload-pdf/", UploadPDFView.as_view(), name="upload-pdf"),
    path("documents/", DocumentListView.as_view(), name="documents"),
    path("query/", LegalQueryView.as_view(), name="query"),
    path("conversations/", ConversationListCreateView.as_view(), name="conversations"),
    path("conversations/<int:pk>/", ConversationDetailView.as_view(), name="conversation-detail"),
    path("query-history/", QueryHistoryListView.as_view(), name="query-history"),
    path("crawl-law-commission/", CrawlLawCommissionView.as_view(), name="crawl-law-commission"),
]
