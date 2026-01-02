python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uuid, random, time

app = FastAPI()

# In-memory session store (swap for DB later)
sessions = {}

def create_session(phone):
session_id = str(uuid.uuid4())
otp = str(random.randint(100000, 999999))
sessions[session_id] = {
"phone": phone,
"otp": otp,
"attempts": 0,
"verified": False,
"created": time.time()
}
return session_id, otp


# ========== AUTO FRAUD TRIGGER ==========
@app.post("/fraud/trigger")
async def fraud_trigger(data: dict):
phone = data["phone"]
session_id, otp = create_session(phone)
return {"session_id": session_id, "status": "auto_started"}


# ========== MANUAL FRAUD TRIGGER ==========
@app.post("/fraud/manual-call")
async def manual_call(data: dict):
phone = data["phone"]
session_id, otp = create_session(phone)
return {"session_id": session_id, "status": "manual_started"}


# ========== VONAGE ANSWER ==========
@app.get("/answer")
async def answer(session_id: str):
return JSONResponse([
{"action": "talk", "text":
"This is an automated fraud prevention call. "
"We detected unusual activity on your account."},
{"action": "talk", "text":
"Please enter the 6 digit code sent to your phone."},
{"action": "input",
"maxDigits": 6,
"eventUrl": [f"https://YOUR_RENDER_URL/verify?session_id={session_id}"]}
])


# ========== OTP VERIFY ==========
@app.post("/verify")
async def verify(request: Request, session_id: str):
data = await request.json()
entered = data["dtmf"]["digits"]
session = sessions.get(session_id)

if not session:
return [{"action": "talk", "text": "Session expired."}]

session["attempts"] += 1

if entered == session["otp"]:
session["verified"] = True
return [{"action": "talk", "text": "Verification successful. Thank you."}]

if session["attempts"] >= 3:
return [{"action": "talk",
"text": "Verification failed. Your account remains protected."}]

return [
{"action": "talk",
"text": "Incorrect code. Please enter your birth month and day. Example: zero one zero five."},
{"action": "input",
"maxDigits": 4,
"eventUrl": [f"https://YOUR_RENDER_URL/verify-dob?session_id={session_id}"]}
]


# ========== DOB VERIFY ==========
@app.post("/verify-dob")
async def verify_dob(request: Request, session_id: str):
data = await request.json()
entered = data["dtmf"]["digits"]

STORED_DOB = "0105" # MMDD example

if entered == STORED_DOB:
sessions[session_id]["verified"] = True
return [{"action": "talk", "text": "Verification complete."}]

return [{"action": "talk",
"text": "Verification failed. Please contact support."}]
