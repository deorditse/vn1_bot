from pydantic_settings import BaseSettings
from app import __version__
from common import env


# from common import env


class ApiConfig(BaseSettings):
    """
    ===================================================================================================================
    Server
    ===================================================================================================================
    """

    api_port: int = env.api_port()
    api_root: str = env.api_root()
    api_is_readonly: bool = env.api_is_readonly()
    api_mode: str = env.api_mode()

    """
    ===================================================================================================================
    Auth
    ===================================================================================================================
    """
    auth_enabled: bool = env.auth_enabled()
    auth_issuer_url: str = env.auth_issuer_url()
    auth_jwks_url: str = env.auth_jwks_url()
    auth_token_url: str = env.auth_token_url()
    auth_client_id: str = env.auth_client_id()
    auth_client_secret: str | None = env.auth_client_secret()
    auth_audience: str | None = env.auth_audience()
    auth_required_roles: list[str] = env.auth_required_roles()

    """
    ===================================================================================================================
    Logging
    ===================================================================================================================
    """
    log_name: str = 'API'
    log_path: str = env.api_log_path()
    log_level: int = env.api_log_level()
    # """
    # ===================================================================================================================
    # Rate limits
    # ===================================================================================================================
    # """
    # # public_limit = env.rate_limit('public')
    # # user_limit = env.rate_limit('user')
    # # doc_limit = env.rate_limit('doc')
    # # key_limit = env.rate_limit('key')
    # # product_limit = env.rate_limit('product')
    # # balance_limit = env.rate_limit('balance')
    # # acquiring_limit = env.rate_limit('acquiring')
    # # admin_limit = env.rate_limit('admin')
    # # upload_limit = env.rate_limit('upload')
    # # download_limit = env.rate_limit('download')

    """
    ===================================================================================================================
    Info
    ===================================================================================================================
    """
    info_was_printed: bool = False

    def log_info_once(self, use_print=False):
        from common.logger.my_logger import MyLogger


        info = print if use_print else MyLogger.info
        if not self.info_was_printed:
            info("=" * 30)
            info("API config:")
            info(f"  version = {__version__}")
            info(f"  port    = {self.api_port}")
            info(f"  log     = {self.log_path}")
            info("=" * 30)
        self.info_was_printed = True


config = ApiConfig()
