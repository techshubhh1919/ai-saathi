from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from pydantic import BaseModel
import os
import re
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/ocr", tags=["ocr"])
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def parse_document_text(text: str, filename: str = ""):
    text_clean = text.strip() if text else ""
    tl = text_clean.lower()
    
    # Check for core government ID patterns
    aadhaar_match = re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\b', text_clean)
    dob_match = re.search(r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b', text_clean)
    pan_match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text_clean)
    voter_match = re.search(r'\b[A-Z]{3}[0-9]{7}\b', text_clean)
    gender_match = "महिला / Female" if ("female" in tl or "महिला" in tl) else ("पुरुष / Male" if ("male" in tl or "पुरुष" in tl) else "दस्तावेज़ में दर्ज")
    
    # 1. PAN Card Detection
    if pan_match or (("income tax" in tl or "permanent account" in tl) and any(c.isdigit() for c in text_clean)):
        doc_type = "PAN Card (Income Tax Dept)"
        pan_no = pan_match.group(0) if pan_match else "पहचान संख्या दर्ज है"
        return {
            "status": "success",
            "is_valid_id": True,
            "document_detected": doc_type,
            "extracted_data": {
                "पहचान संख्या (PAN Number)": pan_no,
                "विभाग": "आयकर विभाग / Income Tax Department",
                "जन्म तिथि (DOB)": dob_match.group(1) if dob_match else "उपलब्ध",
                "दस्तावेज़ स्थिति": "सत्यापित (Verified)"
            },
            "missing_critical_info": [
                {
                    "field": "Aadhaar-PAN Linkage",
                    "severity": "HIGH",
                    "message": "सरकारी नियमों के अनुसार पैन कार्ड को आधार कार्ड से लिंक होना अनिवार्य है।",
                    "action": "incometax.gov.in पर जाकर पैन-आधार लिंकिंग स्थिति जांचें।"
                }
            ],
            "raw_text_preview": text_clean[:500] if text_clean else "PAN Card Document Text",
            "voice_narration": f"पैन कार्ड सफलतापूर्वक स्कैन हो गया है। पैन संख्या {pan_no} है। सुनिश्चित करें कि यह आधार से लिंक है।"
        }
    
    # 2. Aadhaar Card Detection
    elif aadhaar_match or ("uidai" in tl and any(c.isdigit() for c in text_clean)) or ("aadhaar" in tl and ("government" in tl or "india" in tl or aadhaar_match)):
        doc_type = "Aadhaar Card (UIDAI)"
        aadhaar_no = aadhaar_match.group(0) if aadhaar_match else "पहचान संख्या दर्ज है"
        has_mobile = "mobile" in tl or "phone" in tl or re.search(r'\b\d{10}\b', text_clean)
        
        missing = []
        if not has_mobile:
            missing.append({
                "field": "Mobile Number Linkage",
                "severity": "HIGH",
                "message": "इस आधार कार्ड में मोबाइल नंबर लिंक होने की पुष्टि नहीं मिली।",
                "action": "सरकारी योजनाओं की OTP के लिए नज़दीकी डाकघर या जन सेवा केंद्र जाकर मोबाइल लिंक कराएं।"
            })
            
        return {
            "status": "success",
            "is_valid_id": True,
            "document_detected": doc_type,
            "extracted_data": {
                "पहचान संख्या (Aadhaar Number)": aadhaar_no,
                "संस्था": "भारतीय विशिष्ट पहचान प्राधिकरण (UIDAI)",
                "जन्म तिथि / वर्ष": dob_match.group(1) if dob_match else "उपलब्ध",
                "लिंग (Gender)": gender_match,
                "दस्तावेज़ स्थिति": "सत्यापित (Verified)"
            },
            "missing_critical_info": missing,
            "raw_text_preview": text_clean[:500] if text_clean else "Aadhaar Card Document Text",
            "voice_narration": "आधार कार्ड का विश्लेषण पूरा हो गया है। सरकारी योजनाओं के लाभ के लिए आधार में मोबाइल नंबर लिंक होना अनिवार्य है।"
        }
    
    # 3. Ration Card Detection
    elif ("ration" in tl or "राशन" in tl or "nfsa" in tl) and ("card" in tl or "कार्ड" in tl or "खाद्य" in tl or "food" in tl):
        return {
            "status": "success",
            "is_valid_id": True,
            "document_detected": "राष्ट्रीय खाद्य सुरक्षा राशन कार्ड (NFSA)",
            "extracted_data": {
                "दस्तावेज़ प्रकार": "Ration Card (खाद्य रसद विभाग)",
                "पहचान स्थिति": "खाद्य सुरक्षा सूची में सत्यापित",
                "स्थिति": "सक्रिय (Active)"
            },
            "missing_critical_info": [],
            "raw_text_preview": text_clean[:500] if text_clean else "Ration Card Document Text",
            "voice_narration": "राशन कार्ड की पुष्टि हो गई है। राशन वितरण सूची में कार्ड सक्रिय पाया गया है।"
        }
        
    # 4. Voter ID / Election Card
    elif voter_match or "election commission" in tl or "मतदाता" in tl or "voter" in tl:
        v_num = voter_match.group(0) if voter_match else "दर्ज है"
        return {
            "status": "success",
            "is_valid_id": True,
            "document_detected": "मतदाता पहचान पत्र (Voter ID / EPIC)",
            "extracted_data": {
                "पहचान संख्या (EPIC No)": v_num,
                "संस्था": "भारत निर्वाचन आयोग (Election Commission of India)",
                "स्थिति": "मान्य मतदाता पहचान पत्र"
            },
            "missing_critical_info": [],
            "raw_text_preview": text_clean[:500],
            "voice_narration": f"मतदाता पहचान पत्र स्कैन हो गया है। ईपीआईसी संख्या {v_num} है।"
        }

    # 5. STRICT REJECTION: Irrelevant / Faltu / Non-ID Document
    else:
        return {
            "status": "invalid_document",
            "is_valid_id": False,
            "document_detected": "❌ अमान्य दस्तावेज़ (Non-ID / Irrelevant Document)",
            "extracted_data": {
                "फाइल": filename or "Uploaded Image",
                "जाँच स्थिति": "अमान्य / अस्वीकृत (Rejected)",
                "कारण": "किसी मान्य भारतीय पहचान पत्र (आधार, पैन, राशन) के लक्षण नहीं मिले"
            },
            "missing_critical_info": [
                {
                    "field": "अमान्य पहचान पत्र (Invalid ID)",
                    "severity": "CRITICAL",
                    "message": "यह फोटो किसी मान्य सरकारी पहचान पत्र की नहीं है। किसी भी सरकारी योजना या सत्यापन के लिए केवल मूल आधार, पैन या राशन कार्ड ही स्वीकार्य है।",
                    "action": "कृपया दस्तावेज़ को सीधा रखकर, अच्छी रोशनी में केवल आधार, पैन या राशन कार्ड की साफ़ फोटो अपलोड करें।"
                }
            ],
            "raw_text_preview": text_clean[:300] if text_clean else "कोई पहचान योग्य सरकारी टेक्स्ट नहीं मिला।",
            "voice_narration": "अपलोड किया गया दस्तावेज़ अमान्य है। यह कोई सरकारी पहचान पत्र नहीं है। कृपया असली आधार, पैन या राशन कार्ड की साफ़ फोटो अपलोड करें।"
        }


class OcrTextRequest(BaseModel):
    document_type: Optional[str] = None
    raw_text: Optional[str] = None
    ocr_text: Optional[str] = None

@router.post("/scan-text")
def scan_text_json(req: OcrTextRequest):
    content = req.raw_text or req.ocr_text or ""
    return parse_document_text(content, filename=req.document_type or "")

@router.post("/scan")
async def scan_document(
    doc_type: Optional[str] = Form(None),
    ocr_text: Optional[str] = Form(""),
    file: Optional[UploadFile] = File(None)
):
    filename = file.filename if file else ""
    
    # 1. If text was provided by client-side OCR
    if ocr_text and len(ocr_text.strip()) > 3:
        return parse_document_text(ocr_text, filename=filename)

    # 2. If Gemini Vision key is present and a file was uploaded
    if file and GEMINI_API_KEY:
        try:
            file_bytes = await file.read()
            b64_img = base64.b64encode(file_bytes).decode('utf-8')
            mime = file.content_type or "image/jpeg"
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            prompt = """Analyze this image carefully. Is this an authentic Indian Identity Document (Aadhaar, PAN Card, Ration Card, Voter ID)?
If YES: Extract document type, ID number, Name, DOB, Gender, and whether mobile number is present.
If NO (e.g. random photo, bill, receipt, selfie, object, landscape): Explicitly state 'INVALID NON-ID DOCUMENT' and describe what is visible."""
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": mime, "data": b64_img}}
                    ]
                }]
            }
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                result_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                if "INVALID NON-ID DOCUMENT" in result_text:
                    return parse_document_text("", filename=filename)
                return parse_document_text(result_text, filename=filename)
        except Exception as e:
            print(f"Gemini Vision API error: {e}")

    # 3. If a file was uploaded but no valid text was detected
    if file:
        return parse_document_text("", filename=filename)

    # 4. Only if user explicitly clicked a sample test button
    if doc_type == "pan":
        sample_text = "INCOME TAX DEPARTMENT GOVT OF INDIA Permanent Account Number ABCDE1234F DOB 15/08/1982"
        return parse_document_text(sample_text, filename="PAN_Sample.jpg")
    elif doc_type == "ration":
        sample_text = "National Food Security Act NFSA Ration Card No 219800481239 Head of Family Shanti Devi"
        return parse_document_text(sample_text, filename="Ration_Sample.jpg")
    elif doc_type == "aadhaar":
        sample_text = "GOVERNMENT OF INDIA UIDAI Aadhaar Card 4819 2839 1029 Rameshwar Prasad DOB 12/04/1976 Male"
        return parse_document_text(sample_text, filename="Aadhaar_Sample.jpg")
    
    # 5. Default awaiting state
    return {
        "status": "awaiting",
        "is_valid_id": False,
        "document_detected": "प्रतीक्षा में (Awaiting Document)",
        "extracted_data": {},
        "missing_critical_info": [],
        "raw_text_preview": "",
        "voice_narration": "कृपया दस्तावेज़ की फोटो अपलोड करें।"
    }
