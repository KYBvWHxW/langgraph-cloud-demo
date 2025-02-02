import uvicorn
import logging

from .main import app

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8123,
        log_level="info",
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
