import logging as pylog
import platform
import uvicorn
from app.configs import config
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    try:
        uvicorn.run(
            "api.api:app",
            host="localhost" if platform.system() == 'Windows' else "0.0.0.0",
            reload=False,
            proxy_headers=True,
            server_header=True,
            port=config.api_port,
            # forwarded_allow_ips=[],
        )
    except Exception as err:
        pylog.critical(err)
