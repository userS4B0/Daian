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


def generate_datatable(raw_data: List[Any], raw_headers: List[str]) -> str:
    """
    Generates a unified table representation for DAIAN.

    Rules:
    - Ensures the number of headers matches row length.
    - Auto-fills missing headers with empty names.
    - Trims long fields for readability.
    - Removes entirely empty columns automatically.
    - Uses global table formatting from config.
    """

    logger.debug("Generating datatable...")
    logger.debug(f"Raw headers: {raw_headers}")
    logger.debug(f"Raw table data rows: {len(raw_data)}")

    if not raw_data:
        logger.warning("generate_datatable() called with empty raw_data.")
        return "empty table"

    # Normalize headers length to match row width
    max_columns = max(len(row) for row in raw_data)

    if len(raw_headers) < max_columns:
        logger.debug(f"Padding headers: {len(raw_headers)} → {max_columns}")
        raw_headers = raw_headers + [""] * (max_columns - len(raw_headers))

    elif len(raw_headers) > max_columns:
        logger.debug(f"Truncating headers: {len(raw_headers)} → {max_columns}")
        raw_headers = raw_headers[:max_columns]

    # Trim fields if needed for readability
    processed_data = []
    for row in raw_data:
        fixed_row = []
        for field in row:
            fixed_row.append(_trim_field(str(field)))
        processed_data.append(fixed_row)

    logger.debug("Table normalized. Rendering tabulate...")

    # Detect and remove fully empty columns
    _EMPTY_VALUES = ("", None, "-", [], {})
    num_columns = len(raw_headers)


    empty_columns = []

    for column in range(num_columns):
        if all((row[column] in _EMPTY_VALUES) for row in processed_data):
            empty_columns.append[column]

    if empty_columns:
        removed = [raw_headers[column] for column in empty_columns]
        logger.debug(f"Removing empty columns: {removed}")
    
    keep_columns = [column for column in range(num_columns) if column not in empty_columns]
    
    if not keep_columns:
        logger.warning("All columns are empty. Returning minimal table.")
        return "<empty table>"
    
    # Filter headers & rows
    filtered_headers = [raw_headers[i] for i in keep_columns]
    filtered_data = [[row[i] for i in keep_columns] for row in processed_data]

    # Final rendering
    try:
        result = tabulate(
            filtered_data,
            headers=filtered_headers,
            tablefmt=_TABLE_FMT,
        )
        logger.debug("Table generated successfully.")
        return result

    except Exception as e:
        logger.error(f"Failed to render datatable: {e}")
        return f"error rendering table: {e}"
