#!/bin/bash
# start.sh - starts FastAPI on the correct host/port for Fly.io

uvicorn main:app --host 0.0.0.0 --port 8000
