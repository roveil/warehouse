import requests
from requests.exceptions import RequestException

from celery import shared_task
from django.conf import settings
from django.db import transaction
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
    producers_to_create = set()
    new_product_producer = {}

    with transaction.atomic():
        existing_producers = dict(Producer.objects.select_for_update().values_list('name', 'id'))

        for product_pk, product_info, producer_name in csv_data.get_products():

            if producer_name in existing_producers:
                product_info['producer_id'] = existing_producers[producer_name]
            elif producer_name:
                producers_to_create.add(producer_name)
                new_product_producer[product_pk] = producer_name

            product_info['producer_id'] = None
            products_to_update[product_pk] = product_info

        producers_to_create = [{'name': producer_name} for producer_name in producers_to_create]

        if producers_to_create:
            producer_dict = dict(Producer.objects.pg_bulk_create(producers_to_create,
                                                                 returning=['name', 'id']).values_list('name', 'id'))
            for product_pk, producer_name in new_product_producer.items():
                products_to_update[product_pk]['producer_id'] = producer_dict[producer_name]

        updated_product_ids = list(Product.objects.pg_bulk_update_or_create(products_to_update, returning=['id'])
                                   .values_list('id', flat=True))

        if updated_product_ids:
            Product.objects.exclude(id__in=updated_product_ids).delete()
            Producer.objects.exclude(id__in=Product.objects.filter(producer__isnull=False)
                                     .values_list('producer_id', flat=True)).delete()


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
