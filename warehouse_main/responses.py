from typing import Union, List, Dict

from django.http import JsonResponse
from rest_framework.exceptions import APIException


class APIResponse(JsonResponse):
    """
    Любой ответ через API
    """
    STATUS_OK = 200
    STATUS_INVALID_REQUEST = 400
    STATUS_NOT_AUTHENTICATED = 403
    STATUS_SERVER_ERROR = 500

    def __init__(self, data: Union[List, Dict] = None, exception: APIException = None, status: int = None,
                 meta: dict = None):
        self.data = data if data is not None else {}
        self.meta = meta if meta is not None else {}

        if not exception:
            self.meta['status'] = status or self.STATUS_OK
        else:
            self.meta['status'] = status or getattr(exception, 'status_code', self.STATUS_SERVER_ERROR)
            self.meta['error'] = exception.__class__.__name__
            self.meta['error_message'] = exception.detail
            self.meta.update(getattr(exception, 'meta', {}))

        super(APIResponse, self).__init__({"meta": self.meta, "data": self.data}, status=self.meta['status'])

    def generate_response(self) -> JsonResponse:
        response = {"meta": self.meta, "data": self.data}
        return JsonResponse(response, status=self.meta['status'])
