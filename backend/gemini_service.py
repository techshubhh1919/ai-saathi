import os
import requests

SYSTEM_PROMPT = """आप 'एआई साथी' (AI Saathi) हैं — भारत के ग्रामीण व नागरिक सहायकों के लिए एक अत्यंत बुद्धिमान, विनम्र और व्यावहारिक डिजिटल सेवा सहायक।
आपका लक्ष्य है:
1. आम बोलचाल की सरल हिंदी (खड़ी बोली/सहज भाषा) में उत्तर देना।
2. नागरिक के हर सवाल (जैसे मार्कशीट डाउनलोड, आधार, राशन कार्ड, ड्राइविंग लाइसेंस, छात्रवृत्ति, पेंशन, कानूनी मदद आदि) का चरण-दर-चरण (Step 1, Step 2, Step 3), आधिकारिक सरकारी पोर्टल, आवश्यक कागज़ात और टोल-फ्री हेल्पलाइन के साथ सटीक समाधान देना।
3. उत्तर संक्षिप्त, व्यावहारिक और सुनने में आसान रखें ताकि ग्रामीण नागरिक आवाज़ सुनकर सीधे समझ सकें।"""

def call_gemini(prompt: str, custom_key: str = None) -> str:
    key = custom_key or os.getenv("GEMINI_API_KEY")
    if not key:
        return None
        
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{SYSTEM_PROMPT}\n\nनागरिक का सवाल: {prompt}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 450
            }
        }
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, headers=headers, json=payload, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"Gemini API notice: {e}")
        
    return None
