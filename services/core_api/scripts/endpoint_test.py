import requests
from gtts import gTTS
import os
import time

QUESTIONS = [
    {"lang": "hi", "text": "मर्डर के लिए सजा क्या है?", "desc": "Hindi (Murder)"},
    {"lang": "ta", "text": "திருட்டு சம்பந்தப்பட்ட சட்டங்கள் என்ன?", "desc": "Tamil (Theft)"},
    {"lang": "es", "text": "¿Cuáles son las condiciones para el divorcio?", "desc": "Spanish (Divorce)"},
    {"lang": "fr", "text": "Puis-je obtenir une libération sous caution ?", "desc": "French (Bail)"},
    {"lang": "bn", "text": "মৌলিক অধিকার গুলো কি কি?", "desc": "Bengali (Fundamental Rights)"}
]

url = "http://127.0.0.1:8001/legal/voice-query"

for idx, q in enumerate(QUESTIONS):
    print(f"\n--- TEST {idx+1}: {q['desc']} ---")
    print(f"Generating voice for: {q['text']}")
    
    # 1. Generate Voice
    test_audio_path = f"test_{q['lang']}.mp3"
    tts = gTTS(text=q['text'], lang=q['lang'])
    tts.save(test_audio_path)
    
    # Wait a bit for filesystem
    time.sleep(0.5)

    # 2. Send over backend via POST
    print("Sending audio to FastAPI backend...")
    try:
        with open(test_audio_path, "rb") as f:
            files = {"file": (test_audio_path, f, "audio/mpeg")}
            # Send without language code so our backend auto-detects
            data = {"language": ""}
            response = requests.post(url, files=files, data=data, timeout=60)
            
        if response.status_code == 200:
            res_json = response.json()
            print("✅ SUCCESS!")
            print(f"🎙️ Transcription: {res_json.get('transcription')}")
            print(f"📜 Answer Text: {res_json.get('answer_text')}")
            print(f"🔊 Audio URL returned: {res_json.get('audio_url')}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")
        
    # 3. Cleanup
    if os.path.exists(test_audio_path):
        os.remove(test_audio_path)
    time.sleep(1)
    
print("\n--- ALL TESTS COMPLETED ---")
