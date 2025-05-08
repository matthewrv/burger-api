import logging

import uvicorn

from app.config import settings

if __name__ == "__main__":
    try:
        uvicorn.run(
            "app.app:create_app",
            factory=True,
            loop="uvloop",
            host="0.0.0.0",
            port=settings.port,
            use_colors=False,
            access_log=False,
            log_level="warning",
            reload=settings.debug,
            reload_dirs="./app" if settings.debug else None,
        )
    except BaseException as e:
        logging.exception(str(e))
        raise
