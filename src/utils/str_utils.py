from typing import List, Any

from tabulate import tabulate

from config.log.logger import setup_logger
from config.config_loader import ConfigLoader

config = ConfigLoader.load_and_validate()

logger = setup_logger(__name__)

_TABLE_FMT = (
    config.get("app", {}).get("display", {}).get("table_fmt", "rounded_outline")
)
_MAX_FIELD_LENGTH = 50


def _trim_field(value: str, max_len: int = _MAX_FIELD_LENGTH) -> str:
    """Trim strings for table display and append ellipsis."""
    if not isinstance(value, str):
        return value

    if len(value) <= max_len:
        return value

    return value[: max_len - 3] + "..."


def generate_datatable(table_data: List[Any], table_headers: List[str]) -> str:
    """
    Generates a unified table representation for DAIAN.

    Rules:
    - Ensures the number of headers matches row length.
    - Auto-fills missing headers with empty names.
    - Trims long fields for readability.
    - Uses global table formatting from config.
    """

    logger.debug("Generating datatable...")
    logger.debug(f"Raw headers: {table_headers}")
    logger.debug(f"Raw table data rows: {len(table_data)}")

    if not table_data:
        logger.warning("generate_datatable() called with empty table_data.")
        return "<empty table>"

    # Normalize headers length to match row width
    max_columns = max(len(row) for row in table_data)

    if len(table_headers) < max_columns:
        logger.debug(f"Padding headers: {len(table_headers)} → {max_columns}")
        table_headers = table_headers + [""] * (max_columns - len(table_headers))

    elif len(table_headers) > max_columns:
        logger.debug(f"Truncating headers: {len(table_headers)} → {max_columns}")
        table_headers = table_headers[:max_columns]

    # Trim each field
    processed_data = []
    for row in table_data:
        fixed_row = []
        for field in row:
            fixed_row.append(_trim_field(str(field)))
        processed_data.append(fixed_row)

    logger.debug("Table normalized. Rendering tabulate...")

    # Final rendering
    try:
        result = tabulate(
            processed_data,
            headers=table_headers,
            tablefmt=_TABLE_FMT,
        )
        logger.debug("Table generated successfully.")
        return result

    except Exception as e:
        logger.error(f"Failed to render datatable: {e}")
        return f"<error rendering table: {e}>"
