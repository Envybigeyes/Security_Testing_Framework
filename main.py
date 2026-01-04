# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from scripts import SCRIPTS
from storage import verification_sessions, call_logs, dtmf_logs
from auth import require_role
from ui import router as ui_router
import uuid, time, os, io, csv

app = FastAPI()
app.include_router(ui_router)

MAX_OTP_ATTEMPTS = 3

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
        "timestamp": time.time()
    }
    dtmf_logs[session_id] = []
    return session_id

@app.post("/fraud/manual-call")
async def manual_call(data: dict, request: Request):
    require_role(request, "admin")
    session_id = create_session(
        phone=data["phone"],
        otp=data["otp"],
        script=data.get("script", "capital_one"),
        language=data.get("language", "en-US")
    )
    return {"status": "call_started", "session_id": session_id}

@app.get("/answer")
async def answer(session_id: str):
    s = verification_sessions[session_id]
    script = SCRIPTS[s["script"]]["languages"][s["language"]]
    return JSONResponse([
        {"action": "talk", "text": script["intro"]},
        {"action": "talk", "text": script["recording"]},
        {"action": "input",
         "maxDigits": 6,
         "eventUrl": [
             f"https://{os.getenv('FLY_APP_NAME')}.fly.dev/input?session_id={session_id}"
         ]}
    ])

@app.post("/input")
async def input(request: Request, session_id: str):
    data = await request.json()
    digits = data["dtmf"]["digits"]
    s = verification_sessions[session_id]
    script = SCRIPTS[s["script"]]["languages"][s["language"]]
    dtmf_logs[session_id].append(digits)
    if digits == s["otp"]:
        s["verified"] = True
        call_logs[session_id]["result"] = "otp_verified"
        return JSONResponse([
            {"action": "talk", "text": script["menu"]},
            {"action": "input",
             "maxDigits": 1,
             "eventUrl": [
                 f"https://{os.getenv('FLY_APP_NAME')}.fly.dev/menu?session_id={session_id}"
             ]}
        ])
    s["attempts"] += 1
    if s["attempts"] >= MAX_OTP_ATTEMPTS:
        call_logs[session_id]["result"] = "otp_failed"
        return JSONResponse([{"action": "talk", "text": script["fraud"]}])
    return JSONResponse([{"action": "talk", "text": script["retry"]}])

@app.post("/menu")
async def menu(request: Request, session_id: str):
    data = await request.json()
    digit = data["dtmf"]["digits"]
    s = verification_sessions[session_id]
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

@app.get("/export-csv")
async def export_csv():
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["session", "phone", "script", "language", "otp", "result"])
    writer.writeheader()
    for k, v in call_logs.items():
        writer.writerow({"session": k, "phone": v["phone"], "script": v["script"], "language": v["language"], "otp": v["otp"], "result": v["result"]})
    return HTMLResponse(content=output.getvalue(), media_type="text/csv")
