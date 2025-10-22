"""
IFS ECS Logger
--------------

This module provides IFS-compliant structured logging based on
Elastic Common Schema (ECS). It enforces company-level field naming
and structure rules for consistent observability across all CI/CD systems.

Usage Example
-------------

    from ifs_ecs_logger import IFSLogger

    # Initialize logger 
    logger = IFSLogger.get_logger("fetchConfig")

    # Debug - detailed internal state, visible only if level=DEBUG  (ex:  logger = IFSLogger.get_logger("fetchConfig", level="DEBUG") )
    logger.debug("Preparing to fetch configuration file", extra={
        "timestamp": "2025-10-21T12:34:00Z"
    })

    # Info - general progress updates
    logger.info("Starting configuration fetch", extra={
        "hostName": "build-agent-01",
        "timestamp": "2025-10-21T12:34:56Z",
        "http": "200"
    })

    # Warning - non-critical anomalies
    logger.warning("Response took longer than expected", extra={
        "timestamp": "2025-10-21T12:35:10Z",
        "http": {"status_code": 200}
    })

    # Error - operational failures
    logger.error("API call failed", extra={
        "http": {"status_code": 500},
        "timestamp": "2025-10-21T12:35:30Z"
    })

    # Critical - system-level or unrecoverable errors
    logger.critical("Fetch pipeline aborted", extra={
        "timestamp": "2025-10-21T12:36:00Z",
        "hostName": "build-agent-01"
    })

Expected Output (IFS ECS-Compliant JSON)
----------------------------------------
Each log entry will be emitted as structured JSON like:

    {
      "_timestamp": "2025-10-21T12:34:56Z",
      "log.level": "info",
      "message": "Starting configuration fetch",
      "ecs.version": "1.6.0",
      "service.name": "fetchConfig",
      "host": { "name": "build-agent-01" },
      "http": { "response": { "status_code": 200 } }
    }
    
"""


from .logger import IFSLogger
from .formatter import IFSECSFormatter

__all__ = ["IFSLogger", "IFSECSFormatter"]
__version__ = "1.0.0"
__author__ = "Golden CI Development Team"