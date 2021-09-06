import datetime
import requests
from requests.exceptions import RequestException
from typing import Type, Union

from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils.timezone import now
from statsd.defaults.django import statsd

from warehouse.source_interface import SourceInterface, CSVSyncInterface
from warehouse.models import Producer, Product


@shared_task(queue=settings.CELERY_QUEUE, autoretry_for=(Exception,), retry_kwargs={'max_retries': 5},
             retry_backoff=True, ignore_result=True)
def clear_outdated_data(model: Type[Union[Producer, Product]], last_updated_time: datetime) -> None:
    """
    Удаляет записи, время обновления которых, меньше, чем last_updated_time
    :param model: Модель, у которой необходимо удалить устаревшие записи
    :param last_updated_time: Время последнего обновления записей
    :return: None
    """
    while model.objects.filter(updated__lt=last_updated_time)[:1].exists():
        sub_qs = model.objects.filter(updated__lt=last_updated_time).values_list('id', flat=True)[:10000]
        model.objects.filter(id__in=sub_qs).delete()


def _process_sync_product_data(data: SourceInterface) -> None:
    """
    Синхронизирует данные c локальной БД используя интерфейс доступа к данным SourceInterface
    :param data: Интерфейс доступа к данным
    :return: None
    """
    products_to_update = {}
    producers_to_update = set()
    product_producer = {}
    task_time = now()

    for batch in data.get_product_batches():
        with transaction.atomic():
            for product_pk, product_info, producer_name in batch:
                product_info['updated'] = task_time
                products_to_update[product_pk] = product_info

                if producer_name:
                    producers_to_update.add(producer_name)
                    product_producer[product_pk] = producer_name
                else:
                    products_to_update[product_pk]['producer_id'] = None

            # Для того, чтобы не обновлять строки с Producer каждый раз
            current_producers = dict(Producer.objects.filter(name__in=producers_to_update, updated=task_time)
                                     .values_list('name', 'id'))
            producers_updates = [{
                "name": producer_name,
                "updated": task_time
            } for producer_name in producers_to_update if producer_name not in current_producers]
            updated_producers = dict(Producer.objects.pg_bulk_update_or_create(producers_updates, key_fields="name",
                                                                               returning=('name', 'id'))
                                     .values_list('name', 'id'))
            current_producers.update(updated_producers)

            for product_pk, producer_name in product_producer.items():
                products_to_update[product_pk]['producer_id'] = current_producers[producer_name]

            Product.objects.pg_bulk_update_or_create(products_to_update)

        products_to_update.clear()
        producers_to_update.clear()
        product_producer.clear()

    clear_outdated_data.delay(Product, task_time)
    clear_outdated_data.delay(Producer, task_time)


def sync_failed_critical_handler(*_, **__):
    statsd.incr('tasks.process_sync_data_from_google_docs.failed_critical')


@shared_task(queue=settings.CELERY_QUEUE, autoretry_for=(RequestException,), retry_kwargs={'max_retries': 5},
             retry_backoff=True, on_failure=sync_failed_critical_handler, ignore_result=True)
@statsd.timer('tasks.process_sync_data')
def process_sync_data_from_google_docs() -> None:
    """
    Бэкграунд задача, которая синхронизирует данные из csv файла, хранящегося в GoogleDocs с локальной БД
    :return: None
    """
    if not settings.GOOGLE_DOCS_DOCUMENT_URL:
        return

    content = requests.get(settings.GOOGLE_DOCS_DOCUMENT_URL)
    csv_data = CSVSyncInterface(content.text.splitlines(), 'sku (unique id)', 'product_name',
                                'photo_url', 'barcode', 'price_cents', 'producer', batch_size=500)
    _process_sync_product_data(csv_data)
