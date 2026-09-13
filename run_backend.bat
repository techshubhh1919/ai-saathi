@echo off
title AI Saathi - FastAPI Server
echo Starting AI Saathi Backend Server on http://127.0.0.1:8000 ...
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause