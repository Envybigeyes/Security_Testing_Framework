# ui.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from auth import require_role
from storage import call_logs

router = APIRouter()

@router.get("/ui", response_class=HTMLResponse)
async def ui(request: Request):
    require_role(request, "agent")

    rows = ""
    for session_id, data in call_logs.items():
        rows += f"""
        <tr>
            <td>{session_id}</td>
            <td>{data['phone']}</td>
            <td>{data['script']}</td>
            <td>{data['language']}</td>
            <td>{data['result']}</td>
        </tr>
        """

    return f"""
    <html>
    <body>
        <h2>Fraud Verification Dashboard</h2>
        <table border="1">
            <tr>
                <th>Session</th>
                <th>Phone</th>
                <th>Script</th>
                <th>Lang</th>
                <th>Result</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """
