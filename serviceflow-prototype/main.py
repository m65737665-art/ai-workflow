import os
import uvicorn
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from agent import run_agent

app = FastAPI(title="ServiceFlow AI Prototype", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-Memory Datastore for instant zero-dependency running
TECHNICIANS = [
    {
        "id": 1,
        "name": "Marcus Vance",
        "skills": ["HVAC Certified", "Commercial Refrigeration", "Heat Pump Systems"],
        "service_zones": ["North Zone", "Metro Area"],
        "rating": 4.9,
        "hourly_rate": 115,
        "is_active": True
    },
    {
        "id": 2,
        "name": "Elena Rostova",
        "skills": ["Master Electrician", "Industrial Wiring", "Panel Upgrades"],
        "service_zones": ["Downtown", "South Suburbs"],
        "rating": 4.95,
        "hourly_rate": 125,
        "is_active": True
    },
    {
        "id": 3,
        "name": "Carlos Mendez",
        "skills": ["Master Plumber", "Pipe Leak Specialist", "Commercial Drainage"],
        "service_zones": ["West Suburbs", "Metro Area"],
        "rating": 4.85,
        "hourly_rate": 105,
        "is_active": True
    }
]

ENQUIRIES = []
BOOKINGS = []
SENT_EMAILS = []
AUDIT_LOGS = []

def add_log(node: str, message: str, status: str = "SUCCESS"):
    log_entry = {
        "id": len(AUDIT_LOGS) + 1,
        "time": datetime.now().strftime("%H:%M:%S"),
        "node": node,
        "message": message,
        "status": status
    }
    AUDIT_LOGS.insert(0, log_entry)

def seed_demo():
    ENQUIRIES.clear()
    BOOKINGS.clear()
    SENT_EMAILS.clear()
    AUDIT_LOGS.clear()
    
    # Seed 1 initial enquiry awaiting approval so user sees live content immediately
    initial_text = "Server room heat-pump AC is overheating (80F). Need an HVAC tech urgently at 1200 Beacon Blvd, North Zone. Email: robert@techhaven.org, Phone: 555-776-9023"
    state = run_agent(initial_text, enquiry_id=1, technicians=TECHNICIANS, log_fn=add_log)
    ENQUIRIES.append(state)

seed_demo()

# Request schemas
class EnquiryInput(BaseModel):
    raw_message: str

class DecisionInput(BaseModel):
    enquiry_id: int
    action: str  # 'APPROVE', 'REJECT'
    edited_subject: Optional[str] = None
    edited_body: Optional[str] = None

# API Routes
@app.get("/api/state")
def get_full_state():
    return {
        "enquiries": ENQUIRIES,
        "technicians": TECHNICIANS,
        "bookings": BOOKINGS,
        "sent_emails": SENT_EMAILS,
        "logs": AUDIT_LOGS[:20]
    }

@app.post("/api/enquiries")
def create_enquiry(payload: EnquiryInput):
    new_id = len(ENQUIRIES) + 1
    state = run_agent(payload.raw_message, enquiry_id=new_id, technicians=TECHNICIANS, log_fn=add_log)
    ENQUIRIES.insert(0, state)
    return state

@app.post("/api/approve")
def approve_plan(payload: DecisionInput):
    enquiry = next((e for e in ENQUIRIES if e["enquiry_id"] == payload.enquiry_id), None)
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")

    if payload.action == "APPROVE":
        subject = payload.edited_subject or enquiry.get("email_draft_subject", "Booking Confirmation")
        body = payload.edited_body or enquiry.get("email_draft_body", "Confirmed")
        tech = enquiry.get("matched_technician")
        slot = enquiry.get("proposed_slot", {})

        # 1. Execute Gmail Mock Delivery
        email_record = {
            "id": f"msg_{len(SENT_EMAILS)+1}",
            "to": enquiry.get("customer_email") or "customer@example.com",
            "subject": subject,
            "body": body,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "DELIVERED (Gmail API)"
        }
        SENT_EMAILS.insert(0, email_record)

        # 2. Execute Calendar Booking
        booking_record = {
            "id": len(BOOKINGS) + 1,
            "enquiry_id": enquiry["enquiry_id"],
            "technician": tech["name"] if tech else "Assigned Tech",
            "service": enquiry.get("service_type"),
            "slot": slot.get("formatted", "Tomorrow 10:00 AM"),
            "location": enquiry.get("customer_address"),
            "status": "CONFIRMED (Google Calendar)",
            "google_calendar_link": "https://calendar.google.com/calendar/render"
        }
        BOOKINGS.insert(0, booking_record)

        enquiry["status"] = "SCHEDULED"
        add_log("execution", f"Dispatched confirmation email to {email_record['to']} & scheduled Google Calendar event for {booking_record['technician']}.")
        return {"success": True, "message": "Dispatched successfully!", "booking": booking_record}

    elif payload.action == "REJECT":
        enquiry["status"] = "REJECTED"
        add_log("human_approval_gate", f"Operator rejected action plan for Enquiry #{enquiry['enquiry_id']}.", status="WARNING")
        return {"success": True, "message": "Plan rejected"}

@app.post("/api/reset")
def reset():
    seed_demo()
    return {"success": True, "message": "Reset to clean demo data"}

# Serve the static UI
if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    print("[*] ServiceFlow AI Prototype running on http://127.0.0.1:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
