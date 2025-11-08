# app/logger.py
from __future__ import annotations

import logging
from pathlib import Path


def get_logger(name: str = "cerdiot") -> logging.Logger:
    """
    Devuelve un logger configurado. Si ya está configurado, lo devuelve tal cual.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # /opt/iot-backend/logs
    base_dir = Path(__file__).resolve().parent.parent
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / "app.log"

    fmt = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # a fichero
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # a consola
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    return logger


# <<< esto es lo que les faltaba a tus routers >>>
# ahora puedes hacer `from app.logger import logger`
logger = get_logger()
