# ServiceFlow AI – Operations Agent (Prototype Build)

A clean, lightweight, single-folder prototype demonstrating an autonomous AI agent for service business enquiry handling, technician matching, calendar scheduling, and human-in-the-loop dispatching.

---

## ⚡ 10-Second Quick Start

```bash
# 1. Install minimal dependencies (if not already installed)
pip install -r requirements.txt

# 2. Run the server (or double-click run.bat on Windows)
python main.py
```

Now open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser!

> **No Node.js or npm build step required!** The dashboard is rendered directly with zero compilation.

---

## 🎯 What this Prototype Demonstrates

1. **Enquiry Processing:** Ingests raw customer messages, extracting customer name, email, phone, location, urgency, and required skills.
2. **AI Understanding:** Categorizes into service domains (HVAC, Electrical, Plumbing), determines priority scores (1-100), and classifies urgency (`EMERGENCY`, `HIGH`, `MEDIUM`, `LOW`).
3. **Quality & Error Handling:** If critical info (e.g. address or contact details) is missing, the agent flags the issue as `NEEDS_INFO` and automatically drafts a clarification email.
4. **Technician Matching Engine:** Evaluates certified specialists against required skills and geographical zones.
5. **Calendar Integration:** Detects open scheduling windows and suggests conflict-free bookings with Google Calendar links.
6. **AI Action Planning:** Synthesizes draft customer confirmation emails and equipment checklists.
7. **Human-in-the-Loop (HITL) Checkpoint:** Execution is strictly guarded until an operations lead reviews, edits, or approves the plan.
8. **Automated Tool Execution:** Upon approval, executes mock Gmail transmission and Google Calendar booking.
9. **Live Operations Telemetry:** Immutable step-by-step audit trail of all agent decisions.

---

## 📁 Project Structure (Only 4 Files)

```
serviceflow-prototype/
├── main.py          # FastAPI web server, in-memory store & API routes (~150 lines)
├── agent.py         # LangGraph state machine & multi-step agent pipeline (~180 lines)
├── static/
│   └── index.html   # Modern responsive dashboard (Tailwind CDN, zero-build)
├── requirements.txt # Minimal Python packages
├── run.bat          # 1-click Windows launcher
└── README.md
```

---

## 🧪 Interactive Live Demo

Once running on `http://127.0.0.1:8000`, test with 1-click presets:
- **❄️ Server Room HVAC Overheating:** High urgency enquiry matched to Marcus Vance (HVAC Certified).
- **⚡ Warehouse Breaker Sparks:** Emergency electrical hazard matched to Elena Rostova (Master Electrician).
- **🚰 Restaurant Grease Trap Leak:** Commercial plumbing overflow matched to Carlos Mendez (Master Plumber).
- **❓ Incomplete Info Test:** Demonstrates automatic clarification routing when address is omitted.
