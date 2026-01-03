# ui.py
from fastapi.responses import HTMLResponse
from storage import call_logs

def render_dashboard():
    rows = ""
    for sid, v in call_logs.items():
        rows += f"""
        <tr>
            <td>{sid}</td>
            <td>{v['phone']}</td>
            <td>{v['script']}</td>
            <td>{v['language']}</td>
            <td>{v['otp']}</td>
            <td>{v['result']}</td>
        </tr>
        """

    return HTMLResponse(f"""
    <html>
    <body>
        <h2>Verification Operations Dashboard</h2>
        <table border="1">
            <tr>
                <th>Session</th>
                <th>Phone</th>
                <th>Script</th>
                <th>Language</th>
                <th>OTP</th>
                <th>Outcome</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """)
