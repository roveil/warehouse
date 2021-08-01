from typing import Union, Type, Optional

from django.db.models import Model
from rest_framework.views import exception_handler as base_exception_handler

from warehouse_main.exceptions import Error404


def rest_framework_exception_handler(ex, context) -> Optional['APIResponse']:
    """
    Обработчик исключений в API
    :param ex: исключение, генерируемое API
    :param context: словарь с информацией о запросе в котором возникло исключение
    :return: APIResponse
    """
    response = base_exception_handler(ex, context)

    if response:
        response.data = {
            'meta': {
                'error': ex.__class__.__name__,
                'error_message': getattr(ex, 'detail', ''),
                'status': response.status_code
            },
            'data': {}
        }

    return response


def lookup_model(pk: Union[str, int], model_cls: Type[Model]) -> Model:
    """
    Получает объект модели по первичному ключу
    :param pk: Первичный ключ
    :param model_cls: Модель
    :raises Error404: 404 ошибку по api
    :return: объект модели
    """
    try:
        instance = model_cls.objects.get(pk=pk)
    except model_cls.DoesNotExist:
        raise Error404(f"{model_cls.__name__} with primary key '{pk}' does not exists")

    return instance
