import os
import sys
import logging
from .formatter import IFSECSFormatter
from .constants import CONTEXT_ENV_VARS


class IFSLogger:
    """
    IFS ECS Logger
    Provides standardized logging configuration using IFSECSFormatter.
    Injects Tekton/Kubernetes context automatically.
    """

    @staticmethod
    def get_logger(name="ifs", level=None):
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(IFSECSFormatter())

            log_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
            logger.setLevel(getattr(logging, log_level, logging.INFO))
            logger.addHandler(handler)
            logger.propagate = False

            IFSLogger._inject_context(logger)

        return logger

    @staticmethod
    def _inject_context(logger):
        """Attach contextual Tekton/Kubernetes info automatically."""
        def wrap(method):
            def wrapper(msg, *args, **kwargs):
                extra = kwargs.get("extra", {})
                for key in CONTEXT_ENV_VARS:
                    val = os.getenv(key)
                    if val:
                        extra[key.lower()] = val
                kwargs["extra"] = extra
                return method(msg, *args, **kwargs)
            return wrapper

        for level in ("debug", "info", "warning", "error", "critical"):
            setattr(logger, level, wrap(getattr(logger, level)))
