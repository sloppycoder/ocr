from django.db import models


class Statement(models.Model):
    class Meta:
        db_table = "statements"

    name = models.CharField(max_length=64)
    mime_type = models.CharField(max_length=32)
    content = models.BinaryField()
    content_sha = models.CharField(max_length=40, default="")
    submitted_at = models.DateTimeField(auto_now_add=True)
    owner = models.CharField(max_length=64)
