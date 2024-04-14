from django.urls import path

from .views import StatementListView, StatementUploadView

app_name = "statements"

urlpatterns = [
    path("", StatementListView.as_view(), name="index"),
    path("upload", StatementUploadView.as_view(), name="upload"),
]
