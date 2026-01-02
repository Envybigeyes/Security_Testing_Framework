from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uuid, random, time, os
import requests

app = FastAPI()

# --- In-memory verification sessions ---
verification_sessions = {}

def create_verification_session(phone):
session_id = str(uuid.uuid4())
otp = str(random.randint(100000, 999999))
verification_sessions[session_id] = {
"phone": phone,
"otp": otp,
"attempts": 0,
"verified": False,
"created_at": time.time()
}
return session_id, otp

# --- Send OTP (placeholder for SMS integration) ---
def send_sms_otp(phone, otp):
# Example placeholder - integrate Vonage SMS here
print(f"Sending OTP {otp} to {phone}")
# requests.post("https://rest.nexmo.com/sms/json", ...)

# --- Place Vonage call (placeholder) ---
def place_call(phone, session_id):
print(f"Placing call to {phone} with session {session_id}")
# Use Vonage Voice API here

# --- Automatic fraud trigger ---
@app.post("/fraud/trigger")
async def fraud_trigger(data: dict):
phone = data["phone"]
session_id, otp = create_verification_session(phone)
send_sms_otp(phone, otp)
place_call(phone, session_id)
return {"status": "auto_verification_started", "session_id": session_id}

# --- Manual fraud trigger ---
@app.post("/fraud/manual-call")
async def manual_call(data: dict, request: Request):
key = request.headers.get("X-Internal-Key")
if key != os.getenv("INTERNAL_KEY"):
return {"error": "unauthorized"}

phone = data["phone"]
reason = data.get("reason", "manual_fraud_review")
session_id, otp = create_verification_session(phone)
print(f"Manual fraud call triggered: {reason}")
send_sms_otp(phone, otp)
place_call(phone, session_id)
return {"status": "manual_verification_started", "session_id": session_id}

# --- IVR Answer URL ---
@app.get("/answer")
async def answer(session_id: str):
return JSONResponse([
{
"action": "talk",
"text": "This is an automated fraud prevention call. Press 1 to confirm, 2 if this was not you."
},
{
"action": "input",
"maxDigits": 1,
"eventUrl": [f"https://{os.getenv('FLY_APP_NAME')}.fly.dev/input?session_id={session_id}"]
}
])

# --- IVR input handler ---
@app.post("/input")
async def input(request: Request):
data = await request.json()
digit = data.get("dtmf", {}).get("digits")
msg = "Invalid option."
if digit == "1": msg = "Thank you. Verification complete."
if digit == "2": msg = "Alert! Escalating to fraud team."
return JSONResponse([{"action": "talk", "text": msg}])
