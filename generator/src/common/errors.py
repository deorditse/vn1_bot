from abc import ABC

from starlette import status

# https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

"""
===================================================================================================================
Result
===================================================================================================================
"""


class BoolResult:
    def __init__(self, success: bool, code: int = 0, comment: str = ""):
        self.success = success
        self.code = code
        self.comment = comment

    def __bool__(self):
        return self.success


class TrueResult(BoolResult):
    def __init__(self):
        super().__init__(True)


class FalseResult(BoolResult):
    def __init__(self, code: int, comment: str = ""):
        super().__init__(False, code, comment)


"""
=======================================================================================================================
Коды которые возвращает сам FastAPI (Uvicorn)
    200 - OK
    401 - Пользователь не авторизован
    404 - Неверный URL ендпоинта
    405 - Неверный метод GET/POST
    422 - Неверный тип параметра
Каждый код из этого набора может иметь свой набор полей ServerResponse
=======================================================================================================================
"""

"""
=======================================================================================================================
Коды которые возвращает мой API
    400 - Запрашиваемые данные не найдены или неверная логика использования приложения.
          Понять в чем именно ошибся клиент можно по полю ServerResponse['exception'] = DataError/LogicError 
    402 - У пользователя не хватает ресурсов для выполнения операции, 'exception' = BalanceError           
    403 - Пользователь не имеет доступа к функционалу или данным, 'exception' = AccessError
    500 - Произошла ошибка на стороне сервера, 'exception' = CoreError/AdapterError
Все HTTP-ошибки возвращаются через единый протокол из app/api/errors.py
=======================================================================================================================
"""


class MyBaseError(Exception, ABC):
    cause = None
    code_status = None


class DataError(MyBaseError):
    cause = "Запрашиваемые данные не найдены"
    code_status = status.HTTP_404_NOT_FOUND


class LogicError(MyBaseError):
    cause = "Пользователь нарушил логику использования приложения"
    code_status = status.HTTP_400_BAD_REQUEST


class AccessError(MyBaseError):
    cause = "Пользователь не имеет доступа к функционалу или данным"
    code_status = status.HTTP_403_FORBIDDEN


class CoreError(MyBaseError):
    cause = "Произошла ошибка на стороне сервера"
    code_status = status.HTTP_500_INTERNAL_SERVER_ERROR


class AdapterError(MyBaseError):
    cause = "Ошибка при вызове внешнего сервиса"
    code_status = status.HTTP_500_INTERNAL_SERVER_ERROR
