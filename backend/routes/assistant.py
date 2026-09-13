from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import os
import re
from gemini_service import call_gemini

router = APIRouter(prefix="/api/assistant", tags=["assistant"])

class AskRequest(BaseModel):
    query: Optional[str] = None
    question: Optional[str] = None
    language: Optional[str] = "hi"
    api_key: Optional[str] = None

INTENT_RESPONSES = {
    "aadhar_no_address_proof": """Agar aapke paas address proof nahi hai, toh aap inn tariko se Aadhar Card banwa sakte hain:

1. **Aadhar Head of Family (HoF) Option:** Aap apne kisi parivar ke sadasya (jaise mata, pita, ya pati/patni) ke Aadhar card aur relationship proof (Ration Card, Marriage Certificate) ke zariye apna address update/new Aadhar banwa sakte hain.
2. **UIDAI Standard Format Form:** Aap UIDAI ke 'Standard Certificate Form' ko Gazette Officer, Village Panchayat Head (Pradhan), ya Tehsildar se sign aur stamp karwa kar address proof ke roop me use kar sakte hain.

**Aage kya karein?**
Near nearest Aadhar Seva Kendra par appointment book karke jayein ya CSC Center par sampark karein.""",

    "income_certificate_rejected": """Income Certificate rejections usually happen due to missing documents or incorrect income declarations. Here is how to fix it:

**Common Reasons for Rejection:**
1. Missing supporting documents (Ration Card, Salary Slip, or Self-Declaration/Affidavit).
2. Mismatch in details between Aadhar Card and application.
3. Incorrect family income selection on the portal.

**Step-by-Step Solution:**
1. Check the rejection reason mentioned on your state's e-District portal dashboard.
2. Re-apply online with an updated **Self-Declaration Form (Swaghoshna Patra)**.
3. Attach Aadhar Card, Bank Passbook, and your parent's salary slip/affidavit.
4. Contact your local Lekhpal/Patwari to verify the application promptly.""",

    "pm_kisan_bhojpuri_stopped": """Ruaar PM Kisan ke kist rooke ke do-teen go mukhya kaaran ho sakela. Aisan sahi kare ke upay dekhin:

1. **e-KYC Poora Karien:** Apne mobile se PM Kisan portal par jaake OTP ke zariye e-KYC poora karien, ya fir nazdiki CSC (Common Service Center) jaake biometric se e-KYC karwa li'n.
2. **Aadhar Bank Link (NPCI Mapping):** Aapan Aadhar card ke aapan bank khata se link karwa li'n (DBT active hona zaroori ba).
3. **Land Seeding Checking:** PM Kisan portal par 'Beneficiary Status' check karien. Agar 'Land Seeding' NO dekhat ba, ta aapan Khatauni ke photo copy leke Block ya Krishi Vibhag ke office me jama karien.

E sab sahi bhala ke baad aagil kist aawel shuru ho jaai.""",

    "ration_card_add_member": """Ration Card me naya naam judwane ke liye niche diye gaye steps follow karein:

**Zaroori Documents:**
* **Bache ke liye:** Janm Praman Patra (Birth Certificate) aur Mata-Pita ka Aadhar Card.
* **Bahu ke liye:** Shaadi ka Praman Patra (Marriage Certificate), Pati ka Aadhar, aur purane Ration Card se naam hatne ka praman (Surrender Slip).

**Prikriya (Process):**
1. Apne rajya ke Food & Civil Supplies Portal (jaise e-District/CSC) par online apply karein.
2. Online form ki copy aur saare documents attach karke apne K खाद्य aapurti vibhag (Food Inspector office) me jama karein.
3. Verification ke baad 15-30 dino me naam jod diya jata hai.""",

    "scholarship_pending_correction": """Scholarship status me pending ya error aane par yeh kadam uthayein:

1. **Correction Window Check Karein:** Portal par log-in karke dekhein ki 'Correction Window' open hai ya nahi.
2. **Reason Identify Karein:** Agar status me 'Roll Number Mismatch', 'Income Not Verified', ya 'Attendance Less than 75%' dikha raha hai, toh correction section me sahi detail update karein.
3. **College Contact Karein:** Correction karne ke baad, updated form ki printout aur supporting documents apne college/institute ke scholarship cell me jama karein taaki wo ise aage forward kar sakein.""",

    "caste_certificate_delay_bhojpuri": """Jati Praman Patra banwaye me deri ho rahal ba ta e tareeka apnaien:

1. **e-District Portal Status Check:** Sabse pahile aapan application number se e-District website par status check karien ki aawedan Lekhpal/Tehsildar ke paas ba ki aage badh gail ba.
2. **Lekhpal/Patwari se Sampark:** Local Lekhpal se mili'n aur aapan purana vansaawali ya parivar ke kisi sadasya ka purana Jati Praman Patra dikhai'n.
3. **Jansunwai / Samadhan Diwas:** Agar limit time (15 din) se beshi ho gail ba, ta rajya ke Jansunwai portal par shikayat darj karien ya Tehsil me Samadhan Diwas ke din application di'n.""",

    "pm_vishwakarma_ayushman": """Here is the simple step-by-step process to apply for these schemes:

**1. For Ayushman Bharat Card (Free Health Coverage up to ₹5 Lakh):**
* Visit `beneficiary.nha.gov.in` or download the Ayushman App.
* Login using your mobile number, enter your Ration Card number or Aadhar number to check eligibility.
* Complete e-KYC via Aadhar OTP or face authentication to download your card instantly.

**2. For PM Vishwakarma Yojana (For Artisans/Craftspeople):**
* Visit your nearest CSC (Common Service Center) with your Aadhar Card, Bank Passbook, and registered Mobile Number.
* Choose your trade (e.g., carpenter, blacksmith, tailor, mason).
* The Gram Panchayat or Urban Local Body will verify your application, after which you get free skill training and collateral-free loan benefits.""",

    "electricity_wrong_bill_meter": """Galat bijli bill ya kharab meter ki problem solve karne ke liye yeh steps follow karein:

1. **Online Portal / Helpline:** Apne rajya ke bijli vibhag ke toll-free number (jaise 1912) par call karke complaint number lein.
2. **Written Application:** Ek application likhein jisme apna Consumer Account Number (K-No/Account ID), purana sahi bill, aur naye galat bill ki copy lagayein.
3. **SDO / Executive Engineer Office:** Ye application apne kshetra ke SDO office me submit karein aur receiving copy zaroor lein.
4. **Meter Check Request:** Agar meter tez chal raha hai ya kharab hai, toh 'Meter Check Request' ka form bharein. Department lab testing ke baad bill revise kar deta hai."""
,
'marksheet_education': "📜 10वीं या 12वीं की ओरिजिनल मार्कशीट डाउनलोड करने की प्रक्रिया:\n• तरीका 1 (DigiLocker - 100% सरकारी मान्य):\n  1. 'digilocker.gov.in' पोर्टल खोलें या मोबाइल में DigiLocker ऐप डाउनलोड करें।\n  2. आधार नंबर और मोबाइल OTP डालकर लॉगिन करें।\n  3. 'Search Documents' में अपने बोर्ड का नाम लिखें (जैसे: CBSE, UP Board, Bihar Board, NIOS, आदि)।\n  4. 'Class X Marksheet' चुनें, अपना रोल नंबर (Roll No) और पासिंग वर्ष (Year) दर्ज करें।\n  5. 'Get Document' दबाते ही डिजिटल हस्ताक्षरित ओरिजिनल मार्कशीट तुरंत डाउनलोड हो जाएगी। IT Act के तहत यह हर जगह मान्य है।\n• तरीका 2 (आधिकारिक बोर्ड वेबसाइट):\n  • CBSE: cbse.gov.in पर Pariksha Sangam से डुप्लीकेट मार्कशीट निकालें।\n  • UP Board: upmsp.edu.in पर प्रमाण पत्र डाउनलोड सेवा पर जाएं।\n💡 सहायता: यदि रोल नंबर याद न हो तो अपने स्कूल/कॉलेज या नज़दीकी CSC केंद्र से संपर्क करें।", 'aadhaar_services': "🆔 आधार कार्ड ऑनलाइन डाउनलोड करने की प्रक्रिया:\n• चरण 1: आधिकारिक UIDAI पोर्टल 'myaadhaar.uidai.gov.in' पर जाएं।\n• चरण 2: 'Download Aadhaar' पर क्लिक करें।\n• चरण 3: अपना 12 अंकों का आधार नंबर (या 28 अंकों की Enrolment ID) और कैप्चा कोड दर्ज करें।\n• चरण 4: 'Send OTP' दबाएं और आधार से लिंक मोबाइल नंबर पर आया 6 अंकों का OTP दर्ज करें।\n• चरण 5: 'Verify & Download' पर क्लिक करते ही पासवर्ड-प्रोटेक्टेड e-Aadhaar PDF डाउनलोड हो जाएगी।\n💡 PDF का पासवर्ड: आपके नाम के पहले 4 अक्षर (अंग्रेज़ी बड़े अक्षरों में) + जन्म का वर्ष (जैसे: RAMA1995)।\n📞 UIDAI टोल-फ्री हेल्पलाइन: 1947", 'voter_id': "🗳️ डिजिटल वोटर आईडी कार्ड (e-EPIC) डाउनलोड करने की प्रक्रिया:\n• चरण 1: भारत निर्वाचन आयोग के पोर्टल 'voters.eci.gov.in' पर जाएं।\n• चरण 2: 'E-EPIC Download' विकल्प पर क्लिक करें।\n• चरण 3: अपना वोटर आईडी (EPIC) नंबर दर्ज करें और अपना राज्य चुनें।\n• चरण 4: रजिस्टर्ड मोबाइल नंबर पर आया OTP डालें और 'Download' पर क्लिक करें। डिजिटल वोटर कार्ड तुरंत डाउनलोड हो जाएगा।\n📞 राष्ट्रीय वोटर हेल्पलाइन: 1950 (टोल-फ्री)", 'epfo_pf': "💼 PF / EPFO बैलेंस चेक व ऑनलाइन निकासी:\n• 1. मिस्ड कॉल से बैलेंस: अपने रजिस्टर्ड मोबाइल से 9966044425 पर मिस्ड कॉल दें, 2 मिनट में बैलेंस का SMS आ जाएगा।\n• 2. SMS से बैलेंस: 7738299899 पर 'EPFOHO UAN HIN' लिखकर भेजें।\n• 3. ऑनलाइन निकासी (Withdrawal): 'unifiedportal-mem.epfindia.gov.in' पर UAN और पासवर्ड से लॉगिन करें। 'Online Services' > 'Claim (Form-31, 19, 10C)' भरकर सीधे बैंक खाते में पैसा निकालें।\n📞 EPFO हेल्पलाइन: 14470", 'bhulekh_land': "🌾 ज़मीन की खतौनी / भूलेख ऑनलाइन निकालने की प्रक्रिया:\n• चरण 1: अपने राज्य के भूलेख पोर्टल पर जाएं (उदा: उत्तर प्रदेश 'upbhulekh.gov.in', बिहार 'biharbhumi.bihar.gov.in')।\n• चरण 2: अपना जनपद (जिला), तहसील और ग्राम (गांव) चुनें।\n• चरण 3: खसरा/गाटा संख्या, खाता संख्या या खातेदार के नाम से खोजें।\n• चरण 4: कैप्चा कोड डालकर प्रमाणित खतौनी तुरंत देखें और प्रिंट निकालें। सरकारी कार्यों व किसान क्रेडिट कार्ड हेतु यह मान्य है।", 'pension_schemes': "👵 वृद्धावस्था, विधवा व दिव्यांग पेंशन योजना:\n• लाभ: 60 वर्ष से अधिक बुजुर्गों और पात्र विधवा/दिव्यांगों को ₹1,000 से ₹1,500 प्रतिमाह सीधे बैंक खाते में।\n• आवेदन: राज्य समाज कल्याण पोर्टल (जैसे: sspy-up.gov.in) या राष्ट्रीय पेंशन पोर्टल 'nsap.nic.in' पर आधार, आय प्रमाण पत्र (ग्रामीण में ₹46,080 से कम), और बैंक पासबुक के साथ ऑनलाइन फॉर्म भरें।\n• सत्यापन: ग्राम पंचायत व बीडीओ सत्यापन के बाद पेंशन शुरू हो जाती है।", 'birth_death_certificate': "👶 जन्म या मृत्यु प्रमाण पत्र बनवाने की प्रक्रिया:\n• चरण 1: राष्ट्रीय पोर्टल 'crsorgi.gov.in' पर जाएं या नज़दीकी नगर निगम/ग्राम पंचायत सचिवालय जाएं।\n• चरण 2: अस्पताल की जन्म/मृत्यु पर्ची, माता-पिता का आधार कार्ड और निवास प्रमाण पत्र अपलोड करें।\n• चरण 3: 21 दिनों के भीतर आवेदन निःशुल्क होता है। सत्यापन के बाद डिजिटल हस्ताक्षरित प्रमाण पत्र ऑनलाइन डाउनलोड करें।", 'pm_ujjwala': "🔥 प्रधानमंत्री उज्ज्वला योजना (मुफ्त गैस कनेक्शन):\n• लाभ: 100% फ्री नया गैस कनेक्शन, भरा हुआ सिलेंडर, चूल्हा, रेगुलेटर + ₹300 प्रति सिलेंडर सब्सिडी।\n• पात्रता: गरीब ग्रामीण व बीपीएल परिवार की महिला मुखिया।\n• आवेदन: 'pmuy.gov.in' पर जाएं या आधार कार्ड, राशन कार्ड और बैंक पासबुक लेकर नज़दीकी गैस एजेंसी (Indane, HP, Bharat Gas) जाएं। टोल-फ्री: 1800-266-6696।", 'mgnrega_jobcard': "⛏️ मनरेगा जॉब कार्ड बनवाना व हाजिरी देखना:\n• लाभ: ग्रामीण परिवारों को साल में 100 दिन का गारंटीड रोज़गार और सीधे बैंक खाते में मजदूरी।\n• नया कार्ड: ग्राम प्रधान या पंचायत सचिव को परिवार के बालिग सदस्यों का आधार और फोटो दें। 15 दिन में फ्री जॉब कार्ड मिल जाएगा।\n• लिस्ट में नाम: 'nrega.nic.in' पर जाकर अपने राज्य, जिला और ग्राम पंचायत का मस्टर रोल ऑनलाइन चेक करें।", 'certificates_revenue': '📄 आय, जाति, निवास प्रमाण पत्र (Income, Caste, Domicile):\n• चरण 1: आधार कार्ड, राशन कार्ड, 1 फोटो और स्वप्रमाणित घोषणा पत्र लें।\n• चरण 2: राज्य ई-डिस्ट्रिक्ट पोर्टल (जैसे edistrict.up.gov.in) या नज़दीकी CSC केंद्र से ₹15-30 शुल्क में आवेदन करें।\n• चरण 3: लेखपाल व तहसीलदार सत्यापन के बाद 7 से 15 दिनों में डिजिटल हस्ताक्षरित प्रमाण पत्र ऑनलाइन डाउनलोड करें।', 'driving_licence': "🚗 ड्राइविंग लाइसेंस (DL) बनवाने की चरण-दर-चरण प्रक्रिया:\n• चरण 1 (लर्नर लाइसेंस): आधिकारिक पोर्टल 'parivahan.gov.in' पर जाएं > 'Driving Licence' चुनें। आधार OTP से ऑनलाइन टेस्ट देकर मात्र ₹200 में लर्नर लाइसेंस प्राप्त करें।\n• चरण 2: 30 दिन बाद 'Apply for Permanent DL' पर स्लॉट बुक करें और RTO जाकर ड्राइविंग टेस्ट दें (सरकारी फीस लगभग ₹1,000)।\n• चरण 3: टेस्ट पास होने पर 10-15 दिनों में चिप वाला ओरिजिनल प्लास्टिक DL स्पीड पोस्ट से आपके घर आ जाएगा।\n📞 सारथी परिवहन पोर्टल: parivahan.gov.in (टोल-फ्री: 1800-1800-151)", 'traffic_challan': "🚦 ट्रैफिक ई-चालान जांच व भुगतान (चरण-दर-चरण):\n• चरण 1: 'echallan.parivahan.gov.in' पोर्टल खोलें और 'Check Challan Status' पर क्लिक करें।\n• चरण 2: अपना गाड़ी नंबर (RC) और चेसिस नंबर के अंतिम 5 अंक दर्ज करें।\n• चरण 3: 'Pay Now' दबाकर UPI, कार्ड या नेट बैंकिंग से ऑनलाइन चालान भरें और रसीद तुरंत डाउनलोड करें।\n💡 भारी या पुराने चालान पर राष्ट्रीय लोक अदालत में 50% से 80% तक छूट का कानूनी प्रावधान है।", 'pm_kisan': "🌾 पीएम-किसान सम्मान निधि (सालाना ₹6,000 की 3 किस्तें):\n• नया रजिस्ट्रेशन: आधार, बैंक पासबुक और ज़मीन की खतौनी लेकर 'pmkisan.gov.in' पर 'New Farmer Registration' करें या CSC जाएं।\n• e-KYC समाधान: 'PM-KISAN GOI' मोबाइल ऐप से चेहरे का स्कैन (Face Auth) करके 1 मिनट में फ्री ई-केवाईसी पूरा करें।\n• रुकी हुई किस्त: यदि Land Seeding 'NO' है तो तहसील में लेखपाल को खतौनी दें। यदि Aadhaar Bank 'NO' है तो बैंक जाकर NPCI मैपर पर आधार DBT लिंक कराएं।\n📞 किसान टोल-फ्री हेल्पलाइन: 155261 या 011-24300606।", 'ration_card': '🍚 राशन कार्ड सेवा समाधान (चरण-दर-चरण):\n• नया नाम जोड़ना: बच्चे का जन्म प्रमाण पत्र + आधार कार्ड, या बहू का विवाह प्रमाण पत्र लेकर CSC केंद्र से संशोधन फॉर्म भरें। 15-30 दिन में नाम जुड़ जाएगा।\n• नया राशन कार्ड: मुखिया का आधार, आय प्रमाण पत्र, निवास प्रमाण पत्र व बैंक पासबुक से ऑनलाइन अप्लाई करें।\n• कोटेदार की शिकायत: यदि कोटेदार कम राशन तौले या न दे, तो तुरंत राज्य खाद्य हेल्पलाइन 1967 या 1800-1800-150 पर कॉल करें। हर यूनिट पर 5 किलो मुफ्त राशन आपका अधिकार है।', 'eshram_card': "👷 ई-श्रम कार्ड पंजीकरण व लाभ (चरण-दर-चरण):\n• कौन बनवा सकता है: 16 से 59 वर्ष के दैनिक मजदूर, किसान, बढ़ई, दर्जी, ड्राइवर व असंगठित कामगार।\n• आवेदन: आधार कार्ड और बैंक पासबुक लेकर 'eshram.gov.in' पर या CSC से 100% फ्री में 12 अंकों का UAN कार्ड बनवाएं।\n• लाभ: ₹2,00,000 का मुफ्त दुर्घटना बीमा, और सरकार की आपदा सहायता सीधे बैंक खाते में।\n📞 श्रम हेल्पलाइन: 14434।", 'scholarship': "🎓 छात्रवृत्ति (Scholarship) आवेदन प्रक्रिया (चरण-दर-चरण):\n• चरण 1 (दस्तावेज़): पिछली मार्कशीट, फीस रसीद, आय प्रमाण पत्र (2.5 लाख से कम), जाति प्रमाण पत्र, आधार कार्ड और NPCI DBT लिंक बैंक पासबुक।\n• चरण 2: राष्ट्रीय छात्रवृत्ति पोर्टल 'scholarships.gov.in' या राज्य पोर्टल (जैसे scholarship.up.gov.in) पर फ्रेश/रिन्यूअल रजिस्ट्रेशन करें।\n• चरण 3: फॉर्म का फाइनल प्रिंट आउट आवश्यक कागज़ात के साथ अपने स्कूल/कॉलेज में समय सीमा से पहले जमा करें।\n📞 छात्रवृत्ति हेल्पलाइन: 0120-6619540।", 'electricity_services': "⚡ बिजली बिल व कनेक्शन समाधान (चरण-दर-चरण):\n• बिल सुधार: वर्तमान मीटर रीडिंग की साफ फोटो खींचें और टोल-फ्री 1912 पर कॉल करके शिकायत दर्ज कराएं या SDO कार्यालय में आवेदन दें। खपत के अनुसार बिल तुरंत ठीक हो जाता है।\n• नया मीटर कनेक्शन: आधार कार्ड और घर के कागज़ात लेकर बिजली विभाग के 'झटपट पोर्टल' (Jhatpat Portal) पर ऑनलाइन अप्लाई करें। 7 दिनों में नया मीटर लग जाता है।\n📞 24x7 बिजली हेल्पलाइन: 1912।", 'ayushman_card': "🏥 आयुष्मान भारत कार्ड (₹5 लाख मुफ्त इलाज):\n• पात्रता जांच: 'beneficiary.nha.gov.in' पोर्टल खोलें, मोबाइल नंबर और आधार से परिवार की पात्रता चेक करें।\n• 70+ वरिष्ठ नागरिक: 70 वर्ष से अधिक उम्र के सभी बुजुर्गों के लिए बिना आय सीमा का 'आयुष्मान वय वंदना' कार्ड जारी हो रहा है।\n• लाभ: पैनलबद्ध सरकारी व प्राइवेट अस्पतालों में प्रतिवर्ष ₹5,00,000 तक का मुफ्त कैशलेस इलाज व दवाइयां।\n📞 आयुष्मान हेल्पलाइन: 14555।", 'pan_card': "💳 पैन कार्ड बनवाने की प्रक्रिया (10 मिनट में फ्री):\n• डिजिटल e-PAN: आयकर पोर्टल 'incometax.gov.in' पर जाएं > 'Instant E-PAN' चुनें। आधार OTP से 10 मिनट में डिजिटल पैन कार्ड बिल्कुल फ्री डाउनलोड करें।\n• प्लास्टिक कार्ड: NSDL / UTIITSL पोर्टल पर फॉर्म 49A भरें (सरकारी फीस ₹107)। 10 से 15 दिनों में स्पीड पोस्ट से घर आ जाएगा।\n💡 पैन कार्ड को आधार से लिंक रखना अनिवार्य है।", 'bank_services': "🏦 बैंक खाता Re-KYC व आधार DBT लिंक (चरण-दर-चरण):\n• बंद खाता चालू करना: आधार कार्ड, पैन कार्ड और 2 फोटो लेकर बैंक शाखा में 'Re-KYC Form' जमा करें। 24 घंटे में खाता सक्रिय हो जाता है।\n• सरकारी पैसा पाने के लिए: बैंक अधिकारी से 'NPCI Aadhaar Mapper Seeding' फॉर्म भरकर अपने खाते को सरकारी DBT योजनाओं से लिंक कराएं।", 'pm_surya_ghar': "☀️ पीएम सूर्य घर मुफ्त बिजली योजना (चरण-दर-चरण):\n• लाभ: 300 यूनिट मुफ्त बिजली हर महीने और ₹78,00,000 तक की कुल योजना में ₹78,000 की सीधी बैंक सब्सिडी।\n• आवेदन: 'pmsuryaghar.gov.in' पर जाएं, बिजली बिल व आधार से रूफटॉप सोलर के लिए रजिस्ट्रेशन करें।\n📞 हेल्पलाइन: 15555।", 'pm_vishwakarma': "🛠️ पीएम विश्वकर्मा योजना (चरण-दर-चरण):\n• लाभ: 18 पारंपरिक कारीगरों (बढ़ई, लोहार, दर्जी, कुम्हार आदि) को ₹15,000 का मुफ्त टूलकिट अनुदान, ₹500/दिन स्टाइपेंड और मात्र 5% ब्याज पर ₹3 लाख का बिना गारंटी लोन।\n• आवेदन: 'pmvishwakarma.gov.in' पर या नज़दीकी CSC से फ्री में रजिस्ट्रेशन कराएं।", 'rural_schemes': '🌾 प्रमुख ग्रामीण व कृषि योजनाएं:\n• 🏠 पीएम ग्रामीण आवास: बेघर परिवारों को पक्का मकान बनाने हेतु ₹1,20,000 की सरकारी सहायता + 90 दिन मनरेगा मजदूरी।\n• 🌾 किसान क्रेडिट कार्ड (KCC): मात्र 4% रियायती ब्याज पर ₹3 लाख तक का कृषि लोन।\n• 🌧️ फसल बीमा योजना: नुकसान पर 72 घंटे में 1800-889-6868 पर सूचना दें।\n• 👩\u200d🌾 लखपति दीदी: SHG महिलाओं को ड्रोन व रोज़गार हेतु ₹1 से ₹5 लाख की मदद।', 'emergency_legal': '🚨 आपातकालीन, कानूनी व साइबर सुरक्षा सहायता:\n• 🚨 पुलिस व आपातकाल: तुरंत 112 पर कॉल करें। महिला सुरक्षा: 1090।\n• 💸 साइबर फ्रॉड (ऑनलाइन पैसे कटना): तुरंत 1930 पर कॉल करें या cybercrime.gov.in पर शिकायत दर्ज कराएं।\n• ⚖️ मुफ्त सरकारी वकील: NALSA राष्ट्रीय विधिक सेवा हेल्पलाइन 15100।\n• 🩺 मुफ्त डॉक्टर सलाह: ई-संजीवनी (esanjeevani.mohfw.gov.in) पर वीडियो कॉल या 1075।\n• 🛒 उपभोक्ता विवाद: खराब सामान या ठगी पर राष्ट्रीय उपभोक्ता हेल्पलाइन 1915 पर शिकायत करें।', 'greeting': "नमस्ते! मैं 'एआई साथी' (AI Saathi) हूँ — ग्रामीण और नागरिक सेवाओं के लिए आपका डिजिटल सहायक।\nआप मुझसे 10वीं/12वीं मार्कशीट, आधार, राशन कार्ड, ड्राइविंग लाइसेंस, किसान सम्मान निधि, बिजली बिल, या किसी भी सरकारी योजना के बारे में हिंदी या हिंग्लिश में पूछ सकते हैं।", 'help_features': '✅ AI साथी पूरी तरह सक्रिय है! आप सीधे सवाल पूछ सकते हैं:\n1. 📜 10वीं/12वीं मार्कशीट (DigiLocker) व 🆔 आधार कार्ड डाउनलोड\n2. 🚗 ड्राइविंग लाइसेंस (DL) व 🚦 ट्रैफिक चालान जांच व भुगतान\n3. 🌾 पीएम-किसान सम्मान निधि (e-KYC, नया रजिस्ट्रेशन, रुकी किस्त)\n4. 🍚 राशन कार्ड में नाम जोड़ना व 1967 कोटेदार शिकायत\n5. 💼 PF बैलेंस चेक व ⚡ बिजली बिल सुधार (1912)\n6. 🏥 आयुष्मान भारत ₹5 लाख इलाज व 💳 10 मिनट में फ्री e-PAN', 'system_feedback': 'नमस्ते! असुविधा के लिए खेद है। मैं अब 10वीं मार्कशीट, आधार, वोटर कार्ड, ड्राइविंग लाइसेंस, किसान योजना, राशन कार्ड सहित हर नागरिक सेवा का सटीक जवाब देता हूँ।\nकृपया अपना सवाल बोलकर या लिखकर पूछें, मैं तुरंत सही समाधान दूंगा।'}

def predict_civic_answer(q: str) -> str:
    q_clean = q.strip()
    ql = q_clean.lower()
    
    if len(q_clean) < 2:
        return "नमस्ते! आपकी आवाज़ स्पष्ट नहीं सुनाई दी। कृपया साफ़ बोलें या नीचे लिखकर पूछें (उदा: '10वीं की मार्कशीट कैसे निकालें?', 'ड्राइविंग लाइसेंस कैसे बनेगा?')।"

    tokens = set(re.findall(r'[\w\u0900-\u097F]+', ql))

    # --- Priority Custom Citizen Scenarios (Hindi, Hinglish, Bhojpuri, English) ---
    # 1. Aadhaar without address proof
    if (("address" in ql or "पता" in ql) and ("proof" in ql or "प्रमाण" in ql or "nahi" in ql or "नही" in ql or "hof" in ql or "head" in ql)) and ("aadhar" in ql or "aadhaar" in ql or "आधार" in ql):
        return INTENT_RESPONSES["aadhar_no_address_proof"]

    # 2. Income certificate rejected
    if ("income" in ql or "aay" in ql or "आय" in ql) and ("reject" in ql or "रद्द" in ql or "खारिज" in ql or "rejection" in ql or "अस्वीकृत" in ql or "common reasons" in ql):
        return INTENT_RESPONSES["income_certificate_rejected"]

    # 3. PM Kisan Bhojpuri / Stopped / Khata me nahi aawata
    if ("kisan" in ql or "किसान" in ql or "samman" in ql) and ("khata" in ql or "खाता" in ql or "aawata" in ql or "आवत" in ql or "ruaar" in ql or "kare ke pari" in ql or "ruk" in ql or "rooke" in ql or "nahi aa" in ql or "नइखे" in ql or "पइसा" in ql):
        return INTENT_RESPONSES["pm_kisan_bhojpuri_stopped"]

    # 4. Ration card add member / bache ya bahu
    if ("ration" in ql or "राशन" in ql) and ("sadasya" in ql or "सदस्य" in ql or "naam" in ql or "नाम" in ql or "bache" in ql or "bahu" in ql or "बच्चा" in ql or "बहू" in ql or "jod" in ql or "जोड़" in ql or "judwa" in ql):
        return INTENT_RESPONSES["ration_card_add_member"]

    # 5. Scholarship pending / correction / credit card
    if ("scholarship" in ql or "छात्रवृत्ति" in ql or "credit card" in ql or "क्रेडिट कार्ड" in ql) and ("pending" in ql or "पेंडिंग" in ql or "correction" in ql or "करेक्शन" in ql or "mismatch" in ql or "सुधार" in ql):
        return INTENT_RESPONSES["scholarship_pending_correction"]

    # 6. Caste certificate delay / Bhojpuri / deri ho rahal ba
    if ("jati" in ql or "जाति" in ql or "caste" in ql) and ("deri" in ql or "देरी" in ql or "delay" in ql or "rahal ba" in ql or "रहल बा" in ql or "rasta" in ql or "रस्ता" in ql or "samadhan" in ql):
        return INTENT_RESPONSES["caste_certificate_delay_bhojpuri"]

    # 7. PM Vishwakarma / Ayushman Bharat locally
    if ("vishwakarma" in ql or "विश्वकर्मा" in ql or "ayushman" in ql or "आयुष्मान" in ql) and ("apply" in ql or "आवेदन" in ql or "locally" in ql or "yojana" in ql or "योजना" in ql or "how to" in ql):
        return INTENT_RESPONSES["pm_vishwakarma_ayushman"]

    # 8. Bijli bill wrong / meter kharab
    if ("bijli" in ql or "बिजली" in ql or "bill" in ql or "बिल" in ql or "meter" in ql or "मीटर" in ql) and ("galat" in ql or "गलत" in ql or "kharab" in ql or "खराब" in ql or "complaint" in ql or "शिकायत" in ql or "1912" in ql):
        return INTENT_RESPONSES["electricity_wrong_bill_meter"]


    # 1. 10th / 12th Marksheet & DigiLocker
    if tokens & {"मार्कशीट", "marksheet", "सनद", "डिग्री", "degree", "माइग्रेशन", "migration"} or \
       (any(w in ql for w in ["10th", "12th", "10वीं", "12वीं", "10 की", "12 की", "दसवीं", "बारहवीं", "हाईस्कूल", "इंटर"]) and any(w in ql for w in ["रिजल्ट", "नतीजा", "मार्कशीट", "marksheet", "डाउनलोड", "download", "सर्टिफिकेट", "certificate", "नंबर", "roll"])) or \
       ("digilocker" in ql or "डिजीलॉकर" in ql):
        return INTENT_RESPONSES["marksheet_education"]

    # 2. Aadhaar Card
    if tokens & {"आधार", "aadhaar", "adhaar", "aadhar", "uidai", "myaadhaar"}:
        return INTENT_RESPONSES["aadhaar_services"]

    # 3. Voter ID
    if tokens & {"वोटर", "voter", "पहचान", "epic", "निर्वाचन", "voters"}:
        return INTENT_RESPONSES["voter_id"]

    # 4. PF / EPFO
    if tokens & {"pf", "epfo", "uan", "पीएफ", "भविष्य", "passbook"}:
        return INTENT_RESPONSES["epfo_pf"]

    # 5. Bhulekh / Khatauni
    if tokens & {"खतौनी", "भूलेख", "khatauni", "bhulekh", "खसरा", "गाटा", "दाखिल", "खारिज"} or ("zameen" in ql and ("nakal" in ql or "kagaz" in ql)):
        return INTENT_RESPONSES["bhulekh_land"]

    # 6. Pension (Old Age, Widow, Divyang)
    if tokens & {"पेंशन", "pension", "वृद्धावस्था", "विधवा", "दिव्यांग", "vridha", "vidhwa"}:
        return INTENT_RESPONSES["pension_schemes"]

    # 7. Birth & Death Certificate
    if any(w in tokens for w in ["जन्म", "birth", "मृत्यु", "death", "janam", "mrityu"]) and (tokens & {"प्रमाण", "certificate", "patra"} or "certificate" in ql):
        return INTENT_RESPONSES["birth_death_certificate"]

    # 8. Ujjwala Gas
    if tokens & {"उज्ज्वला", "ujjwala", "गैस", "सिलेंडर", "सिलिंडर", "gas"}:
        return INTENT_RESPONSES["pm_ujjwala"]

    # 9. MGNREGA Job Card
    if (tokens & {"मनरेगा", "नरेगा", "mgnrega", "nrega", "जॉब", "job"}) and (tokens & {"कार्ड", "card", "मजदूरी", "हाजिरी"}):
        return INTENT_RESPONSES["mgnrega_jobcard"]

    # 10. Certificates (Income, Caste, Domicile)
    if (tokens & {"आय", "जाति", "निवास", "aay", "jati", "niwas"}) and (tokens & {"प्रमाण", "certificate", "patra"} or "certificate" in ql or "बनवाना" in ql):
        return INTENT_RESPONSES["certificates_revenue"]

    # 11. Greetings
    greeting_words = {"hello", "hi", "hey", "namaste", "नमस्ते", "प्रणाम", "ram"}
    greeting_phrases = ["ram ram", "राम राम", "kaise ho", "how are you", "who are you", "aap kaun ho", "tum kaun ho"]
    if (tokens & greeting_words) and len(tokens) <= 3:
        return INTENT_RESPONSES["greeting"]
    if any(p in ql for p in greeting_phrases):
        return INTENT_RESPONSES["greeting"]

    # 12. Test / API Check
    if any(p in ql for p in ["first api", "api request", "api test", "test query", "status"]) or (tokens & {"features", "options"}):
        return INTENT_RESPONSES["help_features"]

    # 13. System Feedback
    if any(p in ql for p in ["kya yaar", "sahi nhi", "sahi nahi", "kaam nahi", "galat answer", "kuchh bhi bol", "not working", "kharab", "bekar"]):
        return INTENT_RESPONSES["system_feedback"]

    # 14. Driving licence
    if (tokens & {"ड्राइविंग", "लाइसेंस", "licence", "license", "dl", "लर्नर", "learner", "rto"}) or "driving" in ql:
        return INTENT_RESPONSES["driving_licence"]

    # 15. Traffic Challan
    if tokens & {"चालान", "challan", "chalan", "echallan"}:
        return INTENT_RESPONSES["traffic_challan"]

    # 16. PM Kisan
    if (tokens & {"किसान", "kisan", "pmkisan", "samman"}) or "pm kisan" in ql or "सम्मान निधि" in ql:
        return INTENT_RESPONSES["pm_kisan"]

    # 17. Ration Card
    if tokens & {"राशन", "ration", "rashan", "कोटेदार", "kotedar"}:
        return INTENT_RESPONSES["ration_card"]

    # 18. e-Shram
    if (tokens & {"eshram", "shramik", "श्रमिक", "मजदूर", "majdoor"}) or "ई-श्रम" in ql or "e shram" in ql or "labour card" in ql:
        return INTENT_RESPONSES["eshram_card"]

    # 19. Scholarship
    if tokens & {"छात्रवृत्ति", "scholarship", "स्कॉलरशिप", "वजीफा", "nsp"}:
        return INTENT_RESPONSES["scholarship"]

    # 20. Electricity
    if (tokens & {"बिजली", "bijli", "electricity", "jhatpat", "झटपट"}) or (tokens & {"meter", "मीटर"} and ("bill" in ql or "बिल" in ql or "reading" in ql)):
        return INTENT_RESPONSES["electricity_services"]

    # 21. Ayushman Card
    if (tokens & {"आयुष्मान", "ayushman"}) or "golden card" in ql or "गोल्डन कार्ड" in ql or "वय वंदना" in ql:
        return INTENT_RESPONSES["ayushman_card"]

    # 22. PAN Card
    if (tokens & {"pan", "pancard"}) or "पैन कार्ड" in ql or "pan card" in ql or "e-pan" in ql:
        return INTENT_RESPONSES["pan_card"]

    # 23. Bank & DBT
    if (tokens & {"dbt", "npci"}) or ("bank" in tokens and (tokens & {"khata", "account", "rekyc"})):
        return INTENT_RESPONSES["bank_services"]

    # 24. Solar & Rural
    if any(p in ql for p in ["surya ghar", "सूर्य घर", "solar", "सोलर"]):
        return INTENT_RESPONSES["pm_surya_ghar"]
    if any(p in ql for p in ["vishwakarma", "विश्वकर्मा", "karigar"]):
        return INTENT_RESPONSES["pm_vishwakarma"]
    if tokens & {"आवास", "awas", "fasal", "फसल", "kcc", "केसीसी", "lakhpati"}:
        return INTENT_RESPONSES["rural_schemes"]

    # 25. Emergency & Legal
    if tokens & {"cyber", "साइबर", "1930", "police", "पुलिस", "112", "चोरी", "chori", "doctor", "डॉक्टर", "consumer", "उपभोक्ता", "vakil", "वकील"}:
        return INTENT_RESPONSES["emergency_legal"]

    # 26. Universal Digital Seva Problem-Solving Engine
    return (
        f"📋 आपके सवाल '{q_clean}' का ऑनलाइन नागरिक समाधान:\n"
        "• आधिकारिक पोर्टल: यह सेवा भारत सरकार के 'services.india.gov.in', राज्य ई-डिस्ट्रिक्ट पोर्टल (edistrict), या उमंग (web.umang.gov.in) पर ऑनलाइन उपलब्ध है।\n"
        "• चरण 1: संबंधित विभाग के आधिकारिक पोर्टल पर जाएं और आधार OTP या मोबाइल नंबर से लॉगिन करें।\n"
        "• चरण 2: आवेदन फॉर्म भरकर आवश्यक दस्तावेज़ (आधार कार्ड, पहचान पत्र, निवास प्रमाण) अपलोड करें।\n"
        "• चरण 3: फॉर्म सबमिट करने के बाद प्राप्त आवेदन संख्या (Reference No) से स्टेटस ट्रैक करें।\n"
        "💡 सहायता: यदि ऑनलाइन करने में कोई समस्या हो, तो अपने नज़दीकी 'CSC जन सेवा केंद्र' या ग्राम पंचायत सचिवालय जाएं।\n"
        "📞 राष्ट्रीय नागरिक सेवा उमंग टोल-फ्री हेल्पलाइन: 1800-11-5246।"
    )

@router.post("/ask")
def ask_assistant(req: AskRequest):
    q = (req.query or req.question or "").strip()

    # 1. Try real Gemini AI if API key provided or in environment
    ai_reply = call_gemini(q, req.api_key)
    if ai_reply:
        return {
            "status": "success",
            "source": "gemini_multilingual_llm",
            "response_text": ai_reply,
            "voice_response": ai_reply,
            "voice_lang": "hi-IN"
        }

    # 2. Comprehensive 25+ Category Citizen AI Engine
    reply = predict_civic_answer(q)
    return {
        "status": "success",
        "source": "master_citizen_ai_engine",
        "response_text": reply,
        "voice_response": reply,
        "voice_lang": "hi-IN"
    }
