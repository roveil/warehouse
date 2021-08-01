import requests
from csv import DictReader
from unittest import mock

from django.conf import settings
from django.test import TransactionTestCase

from warehouse.models import Product, Producer
from warehouse.tasks import process_sync_data_from_google_docs


def delete_side_effect(*_):
    raise ValueError()


class ProcessSyncDataFromGoogleDocsTest(TransactionTestCase):
    fixtures = ['warehouse_producer', 'warehouse_product']

    def test_sync_data_from_google_docs(self):
        process_sync_data_from_google_docs()

        # старые данные были удалены
        self.assertFalse(Product.objects.filter(name="Unit test product").exists())
        self.assertFalse(Producer.objects.filter(name="unexisting producer").exists())

        # количество записей соответствует количеству записей в csv
        reader = DictReader(requests.get(settings.GOOGLE_DOCS_DOCUMENT_URL).text.splitlines())
        self.assertEqual(len(list(reader)), Product.objects.count())

    @mock.patch('django.db.models.QuerySet.delete', side_effect=delete_side_effect)
    def test_sync_data_from_google_docs_atomic(self, _):
        with self.assertRaises(ValueError):
            process_sync_data_from_google_docs()

        # старые данные не были изменены
        self.assertTrue(Product.objects.filter(name="Unit test product").exists())
