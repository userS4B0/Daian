import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ----------------------------------------------------------------------
# Google calendar IDs (defined on .env)
# ----------------------------------------------------------------------
GCAL_ID_MYTASKS=os.getenv("GCAL_ID_MYTASKS")
GCAL_ID_WORK=os.getenv("GCAL_ID_WORK")
GCAL_ID_TIMEMANAGE=os.getenv("GCAL_ID_TIMEMANAGE")
GCAL_ID_PERSONALEVENTS=os.getenv("GCAL_ID_PERSONALEVENTS")

# ----------------------------------------------------------------------
# Default label for non-scheduled tasks
# ----------------------------------------------------------------------
NONSCHEDULED_TASKS_LABEL = "Agendar"

# ----------------------------------------------------------------------
# Default user timezone (defined on .env)
# ----------------------------------------------------------------------
TZ = os.getenv("TZ")
FALLBACK_TZ = "UTC"