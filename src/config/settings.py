import os
from dotenv import load_dotenv

# lOAD ENVIRONMENT VARIABLES
load_dotenv()

TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")

if not TODOIST_API_TOKEN:
    raise ValueError("Missing TODOIST_API_TOKEN in .env")

NONSCHEDULED_TASKS_LABEL = "Agendar"