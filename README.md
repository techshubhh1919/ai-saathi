# 🏛️ AI Saathi (एआई साथी) — ग्रामीण डिजिटल सेवा सहायक

> **Digital Inclusion & Civic AI Assistant for Rural India**  
> *हर गाँव, हर नागरिक का सच्चा डिजिटल साथी*

---

## 📁 Project Architecture & Structure

`	ext
ai-saathi/
│
├── 🌐 index.html                         # [Person B] Full-Working Civic Web App (Voice In/Out)
├── ⚡ run_backend.bat                    # 1-Click Backend Server Launcher (Port 8000)
├── 🚀 open_app.bat                       # 1-Click Web App Launcher
├── 📽️ open_slides.bat                    # 1-Click Presentation Slides Launcher
├── 📖 README.md                          # Project Documentation
│
├── 📁 backend/                           # [Person A] FastAPI Backend & AI Brain
│   ├── main.py                           # FastAPI Server entry point, CORS & route binding
│   ├── requirements.txt                  # Python dependencies
│   ├── gemini_service.py                 # Google Gemini API + offline fallback
│   ├── simulate_whatsapp.py              # WhatsApp Bot demo tester script
│   ├── Dockerfile                        # Docker container config
│   ├── Procfile                          # Cloud hosting entry (Render/Heroku)
│   ├── render.yaml                       # Cloud deployment configuration
│   ├── .env.example                      # API key template (GEMINI_API_KEY)
│   │
│   ├── 📁 data/
│   │   └── schemes.json                  # Government schemes database (PM-Kisan, Ayushman, etc.)
│   │
│   └── 📁 routes/
│       ├── __init__.py
│       ├── assistant.py                  # POST /api/assistant/ask (Voice QA logic)
│       ├── schemes.py                    # GET /api/schemes & POST /api/schemes/eligibility
│       ├── ocr.py                        # POST /api/ocr/scan (Aadhaar/Ration scan + missing info)
│       ├── fraud.py                      # POST /api/fraud-check (Fake electricity/lottery detector)
│       └── whatsapp.py                   # POST /api/whatsapp/webhook (Twilio bot webhook)
│
└── 📁 presentation/                      # [Person B] Pitch & Demo Material
    ├── slides.html                       # Interactive 8-Slide Pitch Deck (F11 fullscreen)
    ├── PITCH_DECK_8_SLIDES.md            # Slide text content for Canva/Google Slides
    └── DEMO_REHEARSAL_SCRIPT.md          # 3-Minute exact rehearsal script (Person A + Person B)
`

---

## 🚀 How to Run (Quick Start)

1. **Start Backend**: Double click 
un_backend.bat  
   *(Server starts at http://127.0.0.1:8000)*
2. **Open Web App**: Double click open_app.bat (or open index.html in Chrome/Edge)
3. **Present Slides**: Double click open_slides.bat (or open presentation/slides.html)
4. **Test WhatsApp Bot**: Open terminal in ackend/ and run:
   `ash
   python simulate_whatsapp.py
   `
# ai-saathi
