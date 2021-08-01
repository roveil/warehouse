from django.db import models
from django_pg_bulk_update.manager import BulkUpdateManager
from django_pg_returning import UpdateReturningMixin


class BaseManager(UpdateReturningMixin, BulkUpdateManager):
    pass


class BaseModel(models.Model):
    """
    Базовый абстрактный класс для всех Django-моделей. Предоставляет дополнительный функционал для работы с моделями.
    """

    class Meta:
        abstract = True

    objects = BaseManager()
