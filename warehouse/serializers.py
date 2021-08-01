from rest_framework import serializers

from warehouse.models import Product, Producer


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'photo_url', 'bar_code', 'price', 'producer')


class ProducerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producer
        fields = ('id', 'name')
