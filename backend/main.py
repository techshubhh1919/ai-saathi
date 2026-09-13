from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from routes import schemes, fraud, ocr, assistant, whatsapp

app = FastAPI(
    title="AI Saathi Backend API",
    description="Rural Voice-First Digital Services Assistant for Schemes, OCR, and Cyber Fraud Detection",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(schemes.router)
app.include_router(fraud.router)
app.include_router(ocr.router)
app.include_router(assistant.router)
app.include_router(whatsapp.router)

# Serve Frontend statically so Chrome/Edge remembers microphone permissions permanently
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Serve static images and files
images_dir = os.path.join(parent_dir, "images")
if os.path.exists(images_dir):
    app.mount("/images", StaticFiles(directory=images_dir), name="images")

@app.get("/")
def serve_index():
    index_file = os.path.join(parent_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"status": "online", "service": "AI Saathi Rural Civic Assistant"}

@app.get("/api/health")
def health():
    return {
        "status": "online",
        "service": "AI Saathi Rural Civic Assistant",
        "helplines": {
            "kisan_call_centre": 1551,
            "cyber_crime": 1930,
            "women_helpline": 1090
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
