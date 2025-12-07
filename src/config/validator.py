from typing import Dict

from config.log.logger import setup_logger

logger = setup_logger(__name__)


class ConfigValidator:
    REQUIRED_USER_FIELDS = [
        "todoist",
        "todoist.api_token",
        "google",
        "google.token_path",
        "google.credentials_path"
    ]

    @staticmethod
    def validate(config: Dict[str, any]) -> bool:
        """
        Simple validation of required fields.
        """

        def exists(path: str) -> bool:
            keys = path.split(".")
            current = config
            for k in keys:
                if not isinstance(current, dict) or k not in current:
                    return False
                current = current[k]
            return True

        missing = []

        for field in ConfigValidator.REQUIRED_USER_FIELDS:
            if not exists(field):
                missing.append(field)

        if missing:
            logger.warning(f"Missing required config fields: {missing}")
            return False

        logger.info("Configuration validated successfully")
        return True
