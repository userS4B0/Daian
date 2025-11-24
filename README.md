# My Daily Planner ⏱️
**Automated Daily Planning from Todoist to Google Calendar**

![Status](https://img.shields.io/badge/status-in_development-yellow)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-green)

---

## 📌 Overview

**My Daily Planner** is a lightweight automation system designed to intelligently organize your daily schedule by analyzing tasks from **Todoist** and placing them into available time slots in **Google Calendar**.

The project aims to simplify daily planning by:
- Reading unassigned tasks from Todoist  
- Estimating complexity and duration  
- Detecting free spaces in your Google Calendar  
- Automatically scheduling tasks into optimal time blocks  
- Keeping your workflow flexible, predictable, and AI-ready  

This project is intentionally built for **expansion**, including future integration of LLMs for task estimation, classification, and optimization.

---

## ✨ Key Features

- 🔍 **Todoist task ingestion** (filters, labels, priorities)  
- 📅 **Google Calendar availability detection**  
- ⏱️ **Simple rule-based duration estimation** (AI optional)  
- 🧠 **Future-ready architecture for AI-powered planners**  
- ♻️ **Modular and clean Python codebase**  
- 🛠️ **Designed for personal automation workflows**  

---

## 🧩 High-Level Workflow

1. **Ingest**  
   - Fetch unplanned tasks from Todoist  
   - Read existing events from Google Calendar  

2. **Classify & Estimate**  
   - Assign duration and complexity  
   - Tag tasks for prioritization  

3. **Plan**  
   - Detect available time windows  
   - Fit tasks dynamically into your schedule  
   - Avoid collisions and overbooking  

4. **Execute**  
   - Create events in Google Calendar  
   - Mark tasks as scheduled in Todoist  
   - Optional: send notifications  

---

## 🗺️ Roadmap (Initial Phase)

### **Phase 1 — Core MVP**
- [X] Implement Todoist API client  
- [ ] Implement Google Calendar API integration  
- [ ] Define rule-based task duration engine  
- [ ] Build availability scanner  
- [ ] Build scheduling logic (basic fit algorithm)  
- [ ] Create CLI entrypoint  
- [ ] Add environment variable loader  

### **Phase 2 — Automation Layer**
- [ ] Add cron/Docker execution support  
- [ ] Improve logging and error handling  
- [ ] Create "dry-run" preview mode  
- [ ] Add configuration YAML  

### **Phase 3 — Intelligence Upgrade (Future)**
- [ ] LLM-based task duration estimation  
- [ ] Natural language complexity classifier  
- [ ] AI-generated daily planning suggestions  
- [ ] Focus-mode time blocking engine  
- [ ] Dashboard or web UI (FastAPI)  

---

## 🛠️ Tech Stack

- **Python 3.10+**
- `requests` / `google-api-python-client`
- `pydantic` for config/schema validation
- `python-dotenv` for environment management
- Optional: `openai` for AI-powered extensions

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/userS4B0/my-dailiy-planner
cd my-dailiy-planner
```

### 2. Create virutal environment
```bash
python -m venv .venv
source .venv/bin/activate # Linux/MacOS
.venv\Scripts\activate # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment varaibles
Copy `.env.example` -> `.env`, then fill in:
```ini
TODOIST_API_TOKEN=...
GOOGLE_CALENDAR_CREDENTIALS_PATH=...
WORKING_HOURS_START=09:00
WORKING_HOURS_END=18:00
```

---

## 🚀 Usage
Run the full pipeline:

```bash
python src/main.py
```

Preview mode (No changes written to calendar)
```bash
python src/main.py --dry-run
```

---

## 🤝 Contributing

Contributions, ideas, and feature requests are welcome.
Feel free to open issues or submit PRs.

---

## 📜 License

MIT License — free to use, modify, and improve.

---