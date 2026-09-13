from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import json
import os

router = APIRouter(prefix="/api/schemes", tags=["schemes"])

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "schemes.json")

def load_schemes():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

class EligibilityQuery(BaseModel):
    category: str # farmer, student, woman, elderly, labour
    annual_income: Optional[str] = "low"
    land_holding: Optional[str] = "small"
    age: Optional[int] = 35

@router.get("")
def get_all_schemes():
    return {"status": "success", "schemes": load_schemes()}

@router.post("/eligibility")
def check_eligibility(query: EligibilityQuery):
    all_schemes = load_schemes()
    matched = []
    
    for s in all_schemes:
        is_match = False
        if query.category == "farmer" and s["category"] == "farmer":
            is_match = True
        elif query.category == "student" and s["category"] == "student":
            is_match = True
        elif query.category == "woman" and s["category"] == "woman":
            is_match = True
        elif query.category == "labour" and s["category"] in ["labour", "health"]:
            is_match = True
        elif s["category"] in ["health", "housing"] and query.annual_income in ["low", "mid"]:
            is_match = True
            
        if is_match:
            matched.append(s)
            
    if not matched:
        matched = [s for s in all_schemes if s["category"] in ["health", "housing"]]

    voice_hindi = f"आपकी प्रोफ़ाइल के अनुसार कुल {len(matched)} सरकारी योजनाएं मिली हैं जिनमें आपको सीधा लाभ मिल सकता है।"
    return {
        "status": "success",
        "matched_count": len(matched),
        "voice_narration": voice_hindi,
        "schemes": matched
    }
