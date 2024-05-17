from django.db import models


class ApiResponse(models.Model):
    class Meta:
        db_table = "ocr_api_responses"

    mime_type = models.CharField(max_length=32)
    content_sha = models.CharField(max_length=40, default="")
    errors = models.CharField(max_length=2048, null=True)
    response = models.BinaryField(null=True)
    response_at = models.DateTimeField(auto_now_add=True)


class Statement(models.Model):
    class Meta:
        db_table = "ocr_statements"

    name = models.CharField(max_length=64)
    mime_type = models.CharField(max_length=32)
    content = models.BinaryField()
    content_sha = models.CharField(max_length=40, default="")
    submitted_at = models.DateTimeField(auto_now_add=True)
    owner = models.CharField(max_length=64)
    api_response = models.ForeignKey(ApiResponse, on_delete=models.SET_NULL, null=True)

    @property
    def response_status(self):
        if self.api_response:
            return "Success" if self.api_response.errors is None else "Error"
        else:
            return "Pending"

    @property
    def sha7(self):
        return self.content_sha[-7:]


class Transaction(models.Model):
    class Meta:
        db_table = "ocr_transactions"

    trx_date = models.DateField(null=True)
    account_num = models.TextField(max_length=12, null=True)
    currency = models.TextField(null=True)
    withdraw_amount = models.DecimalField(null=True, max_digits=20, decimal_places=2)
    deposit_amount = models.DecimalField(null=True, max_digits=20, decimal_places=2)
    balance = models.DecimalField(null=True, max_digits=20, decimal_places=2)
    description = models.TextField(null=True)
    statement = models.ForeignKey(Statement, on_delete=models.SET_NULL, related_name="transactions", null=True)
    raw_entity = models.BinaryField(null=True)

    def __str__(self):
        desc = self.description[:10] if self.description else ""
        return f"{self.trx_date}/{self.account_num}/{self.withdraw_amount}/{self.deposit_amount}/{self.balance}/{desc}"  # noqa E501
