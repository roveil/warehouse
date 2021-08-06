import uuid

from django.db import models
from django.utils.timezone import now

from warehouse_main.base_models import BaseModel


class Producer(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    updated = models.DateTimeField(default=now, db_index=True)


class Product(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=500)
    photo_url = models.CharField(max_length=255, null=True, blank=True)
    bar_code = models.CharField(max_length=10)
    price = models.PositiveIntegerField()
    producer = models.ForeignKey(Producer, null=True, blank=True, on_delete=models.SET_NULL)
    updated = models.DateTimeField(default=now, db_index=True)

    class Meta:
        unique_together = ('producer', 'name')
