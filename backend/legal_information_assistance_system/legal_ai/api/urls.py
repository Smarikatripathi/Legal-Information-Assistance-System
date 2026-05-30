from django.urls import path
from .views import UploadPDFView, LegalQueryView

urlpatterns = [
    path("upload-pdf/", UploadPDFView.as_view()),
    path("query/", LegalQueryView.as_view()),
]