from django.urls import path

from .views import StatementDetailView, StatementListView, StatementUploadView

app_name = "statements"

urlpatterns = [
    path("", StatementListView.as_view(), name="index"),
    path("upload", StatementUploadView.as_view(), name="upload"),
    path("<int:statement_id>/", StatementDetailView.as_view(), name="detail"),
]
