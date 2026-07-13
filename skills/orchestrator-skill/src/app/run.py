import os

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "app.api.api:app",
        host="0.0.0.0",
        port=int(os.getenv("API_PORT", "8020")),
        reload=os.getenv("API_MODE", "prod").lower() == "dev",
        proxy_headers=True,
    )
