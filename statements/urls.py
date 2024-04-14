from django.urls import path

from .views import StatementListView

app_name = "statements"

urlpatterns = [
    path("", StatementListView.as_view()),
]
