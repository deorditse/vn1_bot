from pydantic import BaseModel
from common import MyBaseError, traceback_list
from common.logger.my_logger import MyLogger


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
