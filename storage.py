# storage.py
import time

verification_sessions = {}
call_logs = {}

def create_session(session_id, phone, script, language, otp):
    verification_sessions[session_id] = {
        "phone": phone,
        "script": script,
        "language": language,
        "otp": otp,
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

def update_result(session_id, result):
    if session_id in call_logs:
        call_logs[session_id]["result"] = result
