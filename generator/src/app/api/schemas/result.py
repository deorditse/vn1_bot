from typing import List

from pydantic import BaseModel
from starlette.requests import Request

from common import MyBaseError, traceback_list, ApiMode
from app.config import config
from common.logger.my_logger import MyLogger

"""
===================================================================================================================
Неизвестная ошибка
===================================================================================================================
"""


class ErrorModel(BaseModel):
    exception: str  # Имя класса
    cause: str  # Общее описание причины ошибки
    details: str  # Конкретные данные послужившие возникновению ошибки
    request_url: str  # Какой URL пришел в запросе
    request_method: str  # POST/GET etc
    request_headers: List[str]  # Список заголовков запроса
    traceback: List[str]  # Путь в коде до ошибки, в режиме PROD=[] для безопасности, но в логе есть

    @staticmethod
    def make(err: Exception, req: Request):
        match err:
            case MyBaseError() as se:
                cause = se.cause
            case _:
                cause = 'Причина ошибки неизвестна'

        return ErrorModel(
            exception=err.__class__.__name__,
            cause=cause,
            details=str(err),
            request_url=str(req.url),
            request_method=str(req.method),
            request_headers=[f"{k}: {v}" for k, v in req.headers.items()],
            traceback=traceback_list(err) if config.api_mode == ApiMode.DEV else [],
        )


"""
===================================================================================================================
Результат выполнения запроса
===================================================================================================================
"""


class ResultModel(BaseModel):
    error_code: int = 0
    error_comment: str = ''
    error_details: str = ''
    error_trace: str = ''
    success: bool = True

    @classmethod
    def ok(cls):
        return ResultModel(success=True, error_code=0)

    @classmethod
    def error(cls, err: MyBaseError):
        from app.config import config
        from common import ApiMode
        MyLogger.exception(err)

        if config.api_mode == ApiMode.DEV:
            return ResultModel(
                success=False,
                error_code=err.code_status,
                error_comment=err.cause,
                error_details=str(err),
                error_trace='\n'.join(traceback_list(err))
            )
        else:
            return ResultModel(
                success=False,
                error_code=err.code_status,
                error_comment=err.cause,
            )


"""
===================================================================================================================
Проверка сервиса
===================================================================================================================
"""


class HealthcheckModel(ResultModel):
    name: str = None
    version: str = None
    started: str = None
