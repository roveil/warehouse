from django.conf import settings
from rest_framework import permissions


class AccessPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        access_token = request.data.get('access_token', '') or request.query_params.get('access_token', '')

        return access_token == settings.ACCESS_TOKEN
