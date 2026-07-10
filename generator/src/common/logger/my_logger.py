import logging as pylog
import os


from common import current_time_msk_str, datetime_msk
from app.config import config

from common import traceback_list, CoreError, DataError, AccessError, LogicError
from slowapi.errors import RateLimitExceeded


class MyLogger:
    @classmethod
    def critical(cls, msg, *args, **kwargs):
        pylog.critical(msg, *args, **kwargs)
        cls._notify(f'critical error\nmsg: {msg}\nargs: {args}\nkwargs: {kwargs}')

    @classmethod
    def error(cls, msg, *args, **kwargs):
        pylog.error(msg, *args, **kwargs)
        cls._notify(f'error\nmsg: {msg}\nargs: {args}\nkwargs: {kwargs}')

    @classmethod
    def warning(cls, msg, *args, **kwargs):
        pylog.warning(msg, *args, **kwargs)
        cls._notify(f'warning\nmsg: {msg}\nargs: {args}\nkwargs: {kwargs}')

    @classmethod
    def info(cls, msg, *args, **kwargs):
        pylog.info(msg, *args, **kwargs)

    @classmethod
    def debug(cls, msg, *args, **kwargs):
        pylog.debug(msg, *args, **kwargs)

    @classmethod
    def exception(cls, err: Exception):
        tb = ''.join(traceback_list(err))
        details = f"{err.__class__.__name__}: {err}\n{tb}"
        match err:
            case RateLimitExceeded():
                pylog.warning(str(err))
            case CoreError():
                pylog.critical(details)
            case DataError() | AccessError() | LogicError():
                pylog.warning(details)
            case _:
                pylog.critical(f"Unknown {err.__class__.__name__}: {details}")
        cls._notify(f'exception\ndetails: {details}')

    @classmethod
    def setup(cls, level=None, prefix=""):

        # sentry_sdk.init(
        #     dsn="https://<YOUR_PUBLIC_KEY>@sentry.io/<YOUR_PROJECT_ID>",
        #     integrations=[FastApiIntegration()],
        #     traces_sample_rate=1.0  # Если нужен Distributed Tracing
        # )

        # Formatting
        formatter = pylog.Formatter(
            fmt='%(asctime)s %(name)s:%(levelname)-7s| %(message)s',
            datefmt='%d-%m %H:%M:%S')

        # Timezone MSK
        def time_msk(*_):
            return datetime_msk().timetuple()

        formatter.converter = time_msk

        # Handlers
        if prefix:
            prefix += "_"
        if not os.path.exists(config.log_path):
            os.makedirs(config.log_path)
        ch = pylog.StreamHandler()
        fh = pylog.FileHandler(str(os.path.join(
            config.log_path,
            f"{prefix}{current_time_msk_str()}.log")))
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        pylog.basicConfig(handlers=[ch, fh])

        # Loggers
        root = pylog.root
        slovo_api = pylog.Logger(config.log_name)
        uvi_root = pylog.getLogger("uvicorn")
        uvi_access = pylog.getLogger("uvicorn.access")
        uvi_error = pylog.getLogger("uvicorn.error")
        loggers = [root, uvi_root, uvi_access, uvi_error, slovo_api]

        # Set uvicorn handlers
        for logger in loggers:
            if logger.handlers:
                for h in logger.handlers:
                    logger.removeHandler(h)
                logger.addHandler(fh)
                logger.addHandler(ch)

        # Levels
        level = level or config.log_level
        slovo_api.setLevel(level)
        uvi_access.setLevel(level)
        root.setLevel(level)  # pylog.INFO
        uvi_root.setLevel(level)  # pylog.INFO
        uvi_error.setLevel(level)  # pylog.CRITICAL

    @staticmethod
    def _notify(message: str):
        """
        Отправка оповещения об ошибке в сторонний сервис.
        Если это Exception — отправляем в Sentry с полным traceback.
        Если это строка — отправляем как событие message.
        """
        try:
            # sentry_sdk.capture_message(message)

            # Дополнительно: Telegram/Slack здесь же если нужно
            # # Пример: Telegram Bot API
            # if not config.telegram_bot_token or not config.telegram_chat_id:
            #     return
            #
            # url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
            # payload = {
            #     "chat_id": config.telegram_chat_id,
            #     "text": message,
            #     "parse_mode": "Markdown",
            # }
            # Асинхронно
            # httpx.post(url, json=payload, timeout=5)
            print(f"error {message}"
                  "\n todo: отправка в Telegram/Slack")

        except Exception as e:
            pylog.warning(f"Ошибка при отправке уведомления: {e}")
