import logging
import mimetypes

from django import forms
from django.contrib import messages
from django.views.generic import FormView
from django_tables2 import SingleTableView, tables

from .models import Statement
from .service import save_file

logger = logging.getLogger(__name__)

__ALLOWED_MIME_TYPES__ = ["image/jpeg", "image/png", "application/pdf"]


class StatementTable(tables.Table):
    class Meta:
        model = Statement
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "name",
            "mime_type",
            "sha7",
            "submitted_at",
            "response_status",
        )


class StatementListView(SingleTableView):
    model = Statement
    table_class = StatementTable
    template_name = "statement_list.html"


class FileUploadForm(forms.Form):
    name = forms.CharField(label="name", max_length=60)
    uploaded_file = forms.FileField(label="file")


class StatementUploadView(FormView):
    form_class = FileUploadForm
    template_name = "statements/statement_upload.html"
    success_url = "/statements/"

    def form_valid(
        self,
        form,
    ):
        file_name = form.cleaned_data["name"]
        mime_type, _ = mimetypes.guess_type(file_name)
        try:
            if mime_type in __ALLOWED_MIME_TYPES__:
                uploaded_file = form.cleaned_data["uploaded_file"]
                save_file(file_name=file_name, mime_type=mime_type, file_content=uploaded_file.read())
                messages.info(self.request, f"File {file_name} uploaded")
                return super().form_valid(form)
            else:
                messages.error(self.request, f"File {file_name} has invalid MIME_TYPE {mime_type}")

        except Exception as e:
            messages.error(self.request, f"File {file_name} cannot be processed due to {e}")

        return super().form_invalid(form)
