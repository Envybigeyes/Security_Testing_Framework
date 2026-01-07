# main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from scripts import SCRIPTS
from storage import verification_sessions, call_logs, dtmf_logs, custom_scripts, activity_log
from auth import require_role
from ui import router as ui_router
import uuid, time, os, io, csv
import vonage

app = FastAPI()
app.include_router(ui_router)

MAX_OTP_ATTEMPTS = 3
last_call_time = {}

def check_rate_limit(identifier: str, limit_seconds: int = 10):
    current_time = time.time()
    if identifier in last_call_time:
        if current_time - last_call_time[identifier] < limit_seconds:
            return False
    last_call_time[identifier] = current_time
    return True

def log_activity(action: str, details: str, user: str = "system"):
    activity_log.append({
        "timestamp": time.time(),
        "action": action,
        "details": details,
        "user": user
    })

def create_session(phone, otp, script, language):
    session_id = str(uuid.uuid4())
    verification_sessions[session_id] = {
        "phone": phone,
        "otp": otp,
        "script": script,
        "language": language,
        "attempts": 0,
        "verified": False,
        "created_at": time.time()
    }
    call_logs[session_id] = {
        "phone": phone,
        "script": script,
        "language": language,
        "otp": otp,
        "result": "pending",
        "status": "initializing",
        "timestamp": time.time(),
        "call_uuid": None
    }
    dtmf_logs[session_id] = []
    log_activity("session_created", f"Session {session_id} for {phone}")
    return session_id

@app.post("/fraud/manual-call")
async def manual_call(data: dict, request: Request):
    require_role(request, "admin")
    
    if not check_rate_limit(data["phone"]):
        raise HTTPException(status_code=429, detail="Please wait before making another call")
    
    session_id = create_session(
        phone=data["phone"],
        otp=data["otp"],
        script=data.get("script", "capital_one"),
        language=data.get("language", "en-US")
    )
    
    try:
        client = vonage.Client(
            key=os.getenv("VONAGE_API_KEY"),
            secret=os.getenv("VONAGE_API_SECRET")
        )
        voice = vonage.Voice(client)
        
        response = voice.create_call({
            "to": [{"type": "phone", "number": data["phone"]}],
            "from": {"type": "phone", "number": os.getenv("VONAGE_NUMBER")},
            "answer_url": [f"https://{os.getenv('FLY_APP_NAME')}.fly.dev/answer?session_id={session_id}"]
        })
        
        call_logs[session_id]["call_uuid"] = response.get("uuid")
        call_logs[session_id]["status"] = "calling"
        log_activity("call_initiated", f"Call to {data['phone']}")
        
        return {"status": "call_started", "session_id": session_id, "call_uuid": response.get("uuid")}
    except Exception as e:
        call_logs[session_id]["result"] = "error"
        call_logs[session_id]["status"] = "failed"
        log_activity("call_failed", f"Failed: {str(e)}")
        return {"status": "error", "message": str(e), "session_id": session_id}

@app.get("/answer")
async def answer(session_id: str):
    s = verification_sessions.get(session_id)
    if not s:
        return JSONResponse([{"action": "talk", "text": "Session not found. Goodbye."}])
    
    if s["script"] in custom_scripts:
        script = custom_scripts[s["script"]]["languages"].get(s["language"])
    else:
        script = SCRIPTS[s["script"]]["languages"][s["language"]]
    
    call_logs[session_id]["status"] = "answered"
    
    return JSONResponse([
        {"action": "talk", "text": script["intro"]},
        {"action": "talk", "text": script.get("recording", "This call may be recorded.")},
        {"action": "input",
         "maxDigits": 6,
         "eventUrl": [f"https://{os.getenv('FLY_APP_NAME')}.fly.dev/input?session_id={session_id}"]}
    ])

@app.post("/input")
async def input(request: Request, session_id: str):
    data = await request.json()
    digits = data.get("dtmf", {}).get("digits", "")
    s = verification_sessions.get(session_id)
    
    if not s:
        return JSONResponse([{"action": "talk", "text": "Session not found."}])
    
    if s["script"] in custom_scripts:
        script = custom_scripts[s["script"]]["languages"].get(s["language"])
    else:
        script = SCRIPTS[s["script"]]["languages"][s["language"]]
    
    dtmf_logs[session_id].append(digits)

    if digits == s["otp"]:
        s["verified"] = True
        call_logs[session_id]["result"] = "otp_verified"
        call_logs[session_id]["status"] = "verified"
        return JSONResponse([
            {"action": "talk", "text": script["menu"]},
            {"action": "input",
             "maxDigits": 1,
             "eventUrl": [f"https://{os.getenv('FLY_APP_NAME')}.fly.dev/menu?session_id={session_id}"]}
        ])

    s["attempts"] += 1
    if s["attempts"] >= MAX_OTP_ATTEMPTS:
        call_logs[session_id]["result"] = "otp_failed"
        call_logs[session_id]["status"] = "failed"
        return JSONResponse([{"action": "talk", "text": script["fraud"]}])

    return JSONResponse([
        {"action": "talk", "text": script["retry"]},
        {"action": "input",
         "maxDigits": 6,
         "eventUrl": [f"https://{os.getenv('FLY_APP_NAME')}.fly.dev/input?session_id={session_id}"]}
    ])

@app.post("/menu")
async def menu(request: Request, session_id: str):
    data = await request.json()
    digit = data.get("dtmf", {}).get("digits", "")
    s = verification_sessions.get(session_id)
    
    if not s:
        return JSONResponse([{"action": "talk", "text": "Session not found."}])
    
    if s["script"] in custom_scripts:
        script = custom_scripts[s["script"]]["languages"].get(s["language"])
    else:
        script = SCRIPTS[s["script"]]["languages"][s["language"]]
    
    dtmf_logs[session_id].append(digit)

    if digit == "1":
        call_logs[session_id]["result"] = "confirmed"
        msg = script["safe"]
    elif digit == "2":
        call_logs[session_id]["result"] = "fraud"
        msg = script["fraud"]
    elif digit == "9":
        call_logs[session_id]["result"] = "escalated"
        msg = script["escalate"]
    else:
        msg = script["retry"]

    return JSONResponse([{"action": "talk", "text": msg}])

@app.get("/api/sessions")
async def get_sessions(request: Request):
    require_role(request, "agent")
    return {"sessions": call_logs, "dtmf": dtmf_logs}

@app.get("/api/analytics")
async def get_analytics(request: Request):
    require_role(request, "agent")
    total_calls = len(call_logs)
    successful = sum(1 for log in call_logs.values() if log["result"] == "confirmed")
    in_progress = sum(1 for log in call_logs.values() if log["status"] in ["calling", "active"])
    return {
        "total_calls": total_calls,
        "successful": successful,
        "in_progress": in_progress,
        "success_rate": (successful / total_calls * 100) if total_calls > 0 else 0
    }

@app.post("/api/scripts/custom")
async def add_custom_script(request: Request, data: dict):
    require_role(request, "agent")
    script_id = data.get("id") or str(uuid.uuid4())[:8]
    custom_scripts[script_id] = data
    log_activity("custom_script_added", f"Script {script_id} added")
    return {"status": "success", "script_id": script_id}

@app.get("/api/scripts")
async def get_scripts(request: Request):
    require_role(request, "agent")
    return {**SCRIPTS, **custom_scripts}

@app.get("/api/activity")
async def get_activity(request: Request):
    require_role(request, "agent")
    return activity_log[-50:]

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "vonage_configured": bool(os.getenv("VONAGE_API_KEY")),
        "active_sessions": len(call_logs)
    }

@app.get("/export-csv")
async def export_csv():
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["session", "phone", "script", "language", "otp", "result", "status"])
    writer.writeheader()
    for k, v in call_logs.items():
        writer.writerow({"session": k, "phone": v["phone"], "script": v["script"], "language": v["language"], "otp": v["otp"], "result": v["result"], "status": v.get("status", "unknown")})
    return HTMLResponse(content=output.getvalue(), media_type="text/csv")

@app.get("/")
async def root():
    return {"status": "Security Testing Framework Online"}
