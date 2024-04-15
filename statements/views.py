import logging
import mimetypes

from django import forms
from django.contrib import messages
from django.http import Http404
from django.urls import reverse
from django.utils.html import format_html
from django.views.generic import FormView, TemplateView
from django_tables2 import SingleTableView, tables

from .models import Statement
from .service import get_page_image, save_file

logger = logging.getLogger(__name__)

__ALLOWED_MIME_TYPES__ = ["image/jpeg", "image/png", "application/pdf"]

# this should be in sync urls.py
app_name = "statements"


class StatementTable(tables.Table):
    class Meta:
        model = Statement
        template_name = "django_tables2/bootstrap5.html"
        orderable = False
        fields = ("name", "mime_type", "sha7", "submitted_at", "response_status")

    def render_response_status(self, value, record):
        if value == "Success":
            return format_html(
                '<a href="{}" target="_blank">{}</a>', reverse(f"{app_name}:detail", args=[record.pk]), "View"
            )
        elif value == "Error":
            return record.api_respone.errors[:16]
        elif value == "Pending":
            return "Pending"


class StatementListView(SingleTableView):
    model = Statement
    table_class = StatementTable
    template_name = "statement_list.html"


class FileUploadForm(forms.Form):
    name = forms.CharField(label="name", max_length=60)
    uploaded_file = forms.FileField(label="file")


class StatementUploadView(FormView):
    form_class = FileUploadForm
    template_name = f"{app_name}/statement_upload.html"
    success_url = f"/{app_name}/"

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


class StatementDetailView(TemplateView):
    template_name = f"{app_name}/statement_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        statement_id = kwargs.get("statement_id")
        try:
            statement = Statement.objects.get(id=statement_id)
            context["statement_name"] = statement.name

            page_no = self.request.GET.get("page", "1")
            encoded_img_data, prev_page, next_page = get_page_image(statement, int(page_no))
            context["page_image"] = encoded_img_data
            context["prev_page"] = prev_page
            context["next_page"] = next_page

        except Statement.DoesNotExist:
            raise Http404("Statement does not exist")

        return context
