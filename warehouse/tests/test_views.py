from django.test import TransactionTestCase, override_settings

from warehouse.models import Product

TOKEN = "unit_test_token"


@override_settings(ACCESS_TOKEN=TOKEN)
class GetProductsByProducerTest(TransactionTestCase):
    fixtures = ['warehouse_producer', 'warehouse_product']

    def setUp(self):
        self.url = f'/producer/100500/products?access_token={TOKEN}'

    def test_access_allow(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_access_denied(self):
        response = self.client.get('/producer/100500/products?access_token=invalid_token')
        self.assertEqual(403, response.status_code)

    def test_response(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

        response_data = response.json()['data']
        self.assertEqual(3, len(response_data))

        for product_dict in response_data:
            self.assertTrue(Product.objects.filter(**product_dict).exists())

    def test_pagination_offset(self):
        response = self.client.get(f"{self.url}&offset=1")
        response_data = response.json()['data']

        self.assertEqual(2, len(response_data))
        self.assertListEqual(["0285b967-bbbb-aaaa-dddd-5c797ac7c0a2", "0285b967-cccc-aaaa-dddd-5c797ac7c0a2"],
                             [item['id'] for item in response_data])

    def test_pagination_limit(self):
        response = self.client.get(f"{self.url}&limit=1")
        response_data = response.json()['data']

        self.assertEqual(1, len(response_data))
        self.assertEqual("0285b967-aaaa-aaaa-dddd-5c797ac7c0a2", response_data[0]['id'])

    def test_pagination_offset_limit(self):
        response = self.client.get(f"{self.url}&limit=1&offset=2")
        response_data = response.json()['data']

        self.assertEqual(1, len(response_data))
        self.assertEqual("0285b967-cccc-aaaa-dddd-5c797ac7c0a2", response_data[0]['id'])
