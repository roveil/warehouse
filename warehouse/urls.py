from django.conf.urls import url

from warehouse import views

urlpatterns = [
    url(r'producer/(?P<producer_pk>\d+)/products/?$', views.ProducerProducts.as_view({'get': 'list'})),
    url(r'producers/?$', views.Producers.as_view({'get': 'list'}))
]
