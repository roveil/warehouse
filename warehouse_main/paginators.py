from rest_framework.pagination import LimitOffsetPagination as LibLimitOffsetPagination


class LimitOffsetPagination(LibLimitOffsetPagination):
    default_limit = 10
    max_limit = 10
