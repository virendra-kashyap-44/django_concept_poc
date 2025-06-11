import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField

class PresignedBucket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50)
    user_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    files = ArrayField(models.CharField(max_length=255), default=list, blank=True)

    class Meta:
        db_table = 'presigned_bucket'