import json
import logging
from ecs_logging import StdlibFormatter
from .constants import FIELD_RENAMES, FORBIDDEN_FIELDS


class IFSECSFormatter(StdlibFormatter):
    """
    Custom ECS JSON formatter enforcing IFS ECS rules:
    - Remove forbidden fields
    - Rename timestamp / hostName
    - Replace @timestamp with _timestamp
    - Replace hostName with host.name
    - Ensure host/http objects follow ECS structure
    """

    def format(self, record):
        base = super().format_to_ecs(record)

        # 1️⃣ Remove forbidden system fields
        for field in list(base.keys()):
            if field in FORBIDDEN_FIELDS:
                del base[field]

        # 2️⃣ Replace @timestamp with _timestamp (IFS prefers underscore)
        if "@timestamp" in base:
            base["_timestamp"] = base.pop("@timestamp")

        # 3️⃣ Apply rename mappings (timestamp → _timestamp, hostName → host.name)
        for old, new in FIELD_RENAMES.items():
            if old in base:
                base[new] = base.pop(old)

        # 4️⃣ Normalize host field
        if "host" in base:
            if isinstance(base["host"], str):
                # Convert string host into ECS structure
                base["host"] = {"name": base["host"]}
            elif isinstance(base["host"], dict):
                # Normalize legacy keys inside host
                if "hostName" in base["host"]:
                    base["host"]["name"] = base["host"].pop("hostName")
        else:
            # If hostName exists but no host object
            if "host.name" in base:
                name = base.pop("host.name")
                base["host"] = {"name": name}

        # 5️⃣ Normalize HTTP field
        if "http" in base:
            if isinstance(base["http"], str):
                try:
                    code = int(base["http"])
                except ValueError:
                    code = base["http"]
                base["http"] = {"response": {"status_code": code}}
            elif isinstance(base["http"], dict):
                # Flatten inconsistent HTTP structure if needed
                if "status_code" in base["http"]:
                    base["http"] = {"response": {"status_code": base["http"]["status_code"]}}

        # 6️⃣ Return JSON output (UTF-8 safe)
        return json.dumps(base, ensure_ascii=False)
