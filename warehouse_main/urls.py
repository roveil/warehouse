from django.urls import re_path, include

urlpatterns = [
    re_path('', include('warehouse.urls')),
]

handler404 = 'warehouse_main.views.handler404'
handler500 = 'warehouse_main.views.handler500'
