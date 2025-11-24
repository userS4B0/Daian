import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ----------------------------------------------------------------------
# Todoist API Token
# ----------------------------------------------------------------------
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")
if not TODOIST_API_TOKEN:
    raise ValueError(
        "Missing TODOIST_API_TOKEN in .env. "
        "Please create a .env file with your token."
    )

# ----------------------------------------------------------------------
# Default label for non-scheduled tasks
# ----------------------------------------------------------------------
NONSCHEDULED_TASKS_LABEL = "Agendar"

# ----------------------------------------------------------------------
# Default table format for CLI output using tabulate
# ----------------------------------------------------------------------
DEFAULT_TABLEFORMAT = "rounded_outline"
