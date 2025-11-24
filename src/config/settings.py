import os
from dotenv import load_dotenv

# lOAD ENVIRONMENT VARIABLES
load_dotenv()
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")

if not TODOIST_API_TOKEN:
    raise ValueError("❌ No se encontró TODOIST_TOKEN en el .env")