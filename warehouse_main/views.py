from typing import List

from rest_framework import viewsets

from warehouse_main.exceptions import Error404, Error500
from warehouse_main.paginators import LimitOffsetPagination
from warehouse_main.responses import APIResponse


def handler404(request, *_, **__):
    return APIResponse(exception=Error404(f"Path '{request.path}' not found"))


def handler500(request):
    return APIResponse(exception=Error500())


class BasePaginationView(viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination

    def get_paginated_response(self, serialized_data: List) -> APIResponse:
        """
        Возвращает стандартный ответ API с мета информацией о пагинации
        :param serialized_data: Сериализованные данные
        :return: APIResponse
        """
        paginated_response = super().get_paginated_response(serialized_data)

        return APIResponse(paginated_response.data['results'], meta={
            'count': paginated_response.data['count'],
            'next': paginated_response.data['next'],
            'previous': paginated_response.data['previous']
        })
