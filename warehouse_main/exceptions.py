from rest_framework.exceptions import APIException


class Error500(APIException):
    status_code = 500
    default_detail = "Internal server error"


class Error404(APIException):
    status_code = 404

    def __init__(self, message: str):
        super().__init__(message, self.status_code)
