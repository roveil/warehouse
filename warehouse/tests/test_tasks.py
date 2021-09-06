import requests
from csv import DictReader
from unittest import mock

from django.conf import settings
from django.test import TransactionTestCase
from django.utils.timezone import now
from freezegun import freeze_time
from freezegun.api import datetime_to_fakedatetime

from warehouse.models import Product, Producer
from warehouse.tasks import process_sync_data_from_google_docs, clear_outdated_data


class ProcessSyncDataFromGoogleDocsTest(TransactionTestCase):
    fixtures = ['warehouse_producer', 'warehouse_product']

    @mock.patch('warehouse.tasks.clear_outdated_data', return_value=None)
    def test_sync_data_from_google_docs(self, clear_outdated_data_mock):
        fixtures_product_counter = Product.objects.count()
        test_time = now()

        with freeze_time(test_time):
            process_sync_data_from_google_docs()

        fake_dt = datetime_to_fakedatetime(test_time)

        # Была вызвана таска для удаления старых данных
        # mock.assert_called_with не отрабатывает как должен
        for model in (Product, Producer):
            self.assertIn((model, fake_dt), (mock_call[0] for mock_call in
                                             clear_outdated_data_mock.delay.call_args_list))

        reader = DictReader(requests.get(settings.GOOGLE_DOCS_DOCUMENT_URL).text.splitlines())

        # количество записей соответствует количеству записей в csv + данные fixtures
        self.assertEqual(Product.objects.count(), len(list(reader)) + fixtures_product_counter)


class ClearOutdatedDataTest(TransactionTestCase):
    fixtures = ['warehouse_producer', 'warehouse_product']

    def test_clear(self):
        test_time = now()

        with freeze_time(test_time):
            Product.objects.create(name='clear_test', bar_code='test_code', price=1)
            clear_outdated_data(Product, test_time)
            self.assertFalse(Product.objects.filter(name="Unit test product").exists())
            self.assertTrue(Product.objects.filter(name='clear_test').exists())
