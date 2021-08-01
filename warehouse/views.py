from statsd.defaults.django import statsd

from warehouse.models import Producer, Product
from warehouse.serializers import ProductSerializer, ProducerSerializer
from warehouse_main.responses import APIResponse
from warehouse_main.utils import lookup_model
from warehouse_main.views import BasePaginationView


class ProducerProducts(BasePaginationView):
    queryset = Product.objects.order_by('pk')

    serializer_class = ProductSerializer

    @statsd.timer('warehouse.views.get_products_by_producer')
    def list(self, request, *_, **kwargs) -> APIResponse:
        producer = lookup_model(kwargs['producer_pk'], Producer)
        products_list = self.paginate_queryset(self.get_queryset().filter(producer=producer))
        serialized_data = self.serializer_class(products_list, many=True).data

        return self.get_paginated_response(serialized_data)


class Producers(BasePaginationView):
    queryset = Producer.objects.order_by('pk')
    serializer_class = ProducerSerializer
