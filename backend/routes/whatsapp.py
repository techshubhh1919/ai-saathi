from fastapi import APIRouter, Request, Response
from routes.assistant import predict_civic_answer

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])

@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()
    incoming_msg = form_data.get("Body", "").strip()
    
    if not incoming_msg:
        reply_text = "नमस्ते! मैं एआई साथी हूँ। सरकारी योजनाओं, दस्तावेज़ सहायता, या धोखाधड़ी मैसेज जांच के लिए सीधे अपना सवाल बोलकर या लिखकर भेजें।"
    elif incoming_msg == "1":
        reply_text = "🌾 सरकारी योजनाएं: PM-Kisan (₹6000), आयुष्मान भारत (₹5 लाख मुफ्त इलाज), लाडली बहना (₹1250/माह)। अधिक जानने के लिए योजना का नाम लिखकर भेजें।"
    elif incoming_msg == "2":
        reply_text = "🚨 साइबर सतर्कता: बिजली बिल कटने या लॉटरी के मैसेज 100% फर्जी होते हैं। किसी भी अनजान लिंक पर क्लिक न करें। साइबर हेल्पलाइन: 1930."
    else:
        reply_text = predict_civic_answer(incoming_msg)
        
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply_text}</Message>
</Response>"""
    return Response(content=twiml_response, media_type="application/xml")
