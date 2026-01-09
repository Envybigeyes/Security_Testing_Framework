import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Templates
templates = Jinja2Templates(directory="templates")

# Static files (optional but recommended for UI)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Base URL (used later for Vonage webhooks, etc.)
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "base_url": BASE_URL
        }
    )
