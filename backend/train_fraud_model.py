import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

# 1. Dataset: Rural Indian Scam SMS vs Safe Official SMS
data = [
    # Fraud / Scams (Label: 1 - HIGH_DANGER)
    ('Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM from electricity office. Call officer Mr. Sharma 9876543210', 1),
    ('Bijli ka bill turant bharein warna connection kat jayega. Sampark karein 9811223344', 1),
    ('KBC ALL INDIA SIM CARD LUCKY DRAW ME AAPNE JEETA HAI 25 LAKH CASH PRIZE. WhatsApp call karein 8899001122', 1),
    ('Dear Customer, your SBI YONO account will be blocked today. Please update PAN immediately by downloading APK: bit.ly/sbi-pan-apk', 1),
    ('PM Kisan 17th installment release! Click here to claim your pending Rs 4000: http://pmkisan-claim.xyz', 1),
    ('Congratulations! You have won Rs 50,00,000 in Tata Lottery. Deposit processing fee Rs 5,000 to account', 1),
    ('Electricity bill unpaid. Officer will cut line at 8 PM. Download AnyDesk app for payment verification', 1),
    ('Aapka Ration Card cancel kar diya gaya hai. Chalu karne ke liye is link par click karke biometric update karein', 1),
    ('Urgent: Your SIM card will be deactivated within 24 hours. Call Jio helpline 9823456789 to update KYC', 1),
    ('Pay electricity bill immediately via APK file link http://urja-bill.in/pay.apk to avoid power cut', 1),
    ('PM Mudra Loan approved Rs 5,00,000 without guarantee. Transfer Rs 2,500 file charge immediately', 1),
    ('Dear user, Rs 25,000 lottery credited to your Paytm wallet. Click to accept: http://short.url/paytm', 1),
    ('Your bank account has been suspended due to incomplete KYC. Download RustDesk to verify', 1),

    # Legitimate / Safe Messages (Label: 0 - SAFE)
    ('SBI: Your A/c XXX4819 credited by Rs 2000.00 on 12Sep26 through UPI Ref 42551982. Balance Rs 8420.50', 0),
    ('Dear Customer, OTP for login to your account is 482910. Do not share OTP with anyone. - Bank', 0),
    ('PM-KISAN: 16th installment of Rs 2000 has been transferred to your bank account. Check status at pmkisan.gov.in', 0),
    ('Your monthly electricity bill for meter no 109283 is Rs 450. Due date is 25-Sep-2026. Pay at official portal uppcl.org', 0),
    ('Aadhaar OTP is 918234 for authentication at CSC Center. Valid for 10 minutes. UIDAI', 0),
    ('Dear Student, your NSP Scholarship application has been approved by state nodal officer.', 0),
    ('Ration distribution for the month of September will start from 15th at your village fair price shop.', 0),
    ('HDFC Bank: Rs 1500 debited from A/c 5821 at ATM. Remaining balance Rs 12,300.', 0),
    ('Ayushman Bharat PMJAY: Your Golden Card is generated. Download from official portal.', 0),
    ('Your LPG cylinder booking ref 881923 is confirmed. Expected delivery in 2 days.', 0)
]

df = pd.DataFrame(data, columns=['text', 'label'])

# 2. Build Pipeline: N-Gram TF-IDF Vectorizer + Multinomial Naive Bayes
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1, 2), stop_words='english')),
    ('clf', MultinomialNB())
])

# 3. Train Model
print('Training Fraud Detection Model on Rural Indian Cyber Dataset...')
pipeline.fit(df['text'], df['label'])

# 4. Evaluation
preds = pipeline.predict(df['text'])
acc = accuracy_score(df['label'], preds)
print(f'Accuracy: {acc * 100:.2f}%\n')
print(classification_report(df['label'], preds, target_names=['SAFE', 'HIGH_DANGER']))

# 5. Export Model Artifact
output_path = os.path.join(os.path.dirname(__file__), 'trained_fraud_model.pkl')
joblib.dump(pipeline, output_path)
print(f'Model artifact successfully saved to: {output_path}')
