import requests
from requests.exceptions import RequestException

from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils.timezone import now
from statsd.defaults.django import statsd

from warehouse.csv_source_interface import CSVSyncInterface
from warehouse.models import Producer, Product


def _process_sync_product_data(csv_data: CSVSyncInterface) -> None:
    """
    Синхронизирует данные c локальной БД используя интерфейс доступа к данным CSVSyncInterface
    :param csv_data: Интерфейс доступа к данным csv
    :return: None
    """
    products_to_update = {}
    producers_to_update = set()
    product_producer = {}
    task_time = now()

    for batch in csv_data.get_product_batches():
        with transaction.atomic():
            for product_pk, product_info, producer_name in batch:
                product_info['updated'] = task_time
                products_to_update[product_pk] = product_info

                if producer_name:
                    producers_to_update.add(producer_name)
                    product_producer[product_pk] = producer_name
                else:
                    products_to_update[product_pk]['producer_id'] = None

            producers_updates = [{
                "name": producer_name,
                "updated": task_time
            } for producer_name in producers_to_update]
            updated_producers = dict(Producer.objects.pg_bulk_update_or_create(producers_updates, key_fields="name",
                                                                               returning=('name', 'id'))
                                     .values_list('name', 'id'))
    
            for product_pk, producer_name in product_producer.items():
                products_to_update[product_pk]['producer_id'] = updated_producers[producer_name]
    
            Product.objects.pg_bulk_update_or_create(products_to_update)
        
        products_to_update.clear()
        producers_to_update.clear()
        product_producer.clear()
        
    Product.objects.filter(updated__lt=task_time).delete()
    Producer.objects.filter(updated__lt=task_time).delete()


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
    _process_sync_product_data(CSVSyncInterface(content.text.splitlines(), 'sku (unique id)', 'product_name',
                                                'photo_url', 'barcode', 'price_cents', 'producer'))
