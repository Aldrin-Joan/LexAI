"""
Voice Pipeline End-to-End Test
Tests the full flow: gTTS audio generation → POST /legal/voice-query → Whisper STT →
translate → KG expand → LLM → translate back → gTTS → returns audio URL.
"""
import sys
import io
import requests
import os
import time

# Force UTF-8 output for Windows console (Hindi/non-ASCII characters)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://127.0.0.1:8001"
VOICE_URL = f"{BASE_URL}/legal/voice-query"

# Test cases: multiple languages
QUESTIONS = [
    {
        "lang": "hi",
        "text": "मुझे CBSE board को sue करना है, उसके steps बताओ",
        "desc": "Hindi - CBSE board sue karna (demo query)",
    },
    {
        "lang": "hi",
        "text": "मर्डर के लिए सजा क्या है?",
        "desc": "Hindi - Murder punishment",
    },
    {
        "lang": "ta",
        "text": "திருட்டு சம்பந்தப்பட்ட சட்டங்கள் என்ன?",
        "desc": "Tamil - Theft laws",
    },
    {
        "lang": "bn",
        "text": "মৌলিক অধিকার গুলো কি কি?",
        "desc": "Bengali - Fundamental Rights",
    },
]

def separator(title=""):
    print(f"\n{'='*60}")
    if title:
        print(f"  {title}")
        print(f"{'='*60}")


def run_test(idx, q):
    separator(f"TEST {idx+1}: {q['desc']}")

    # Step 1: Generate a voice file using gTTS
    print(f"[1/3] Generating {q['lang']} audio via gTTS...")
    try:
        from gtts import gTTS
        audio_path = f"_test_{q['lang']}_{idx}.mp3"
        gTTS(text=q['text'], lang=q['lang']).save(audio_path)
        print(f"      Audio saved: {audio_path}")
    except Exception as e:
        print(f"      ERROR generating audio: {e}")
        return

    time.sleep(0.3)

    # Step 2: Send to backend
    print(f"[2/3] Sending to POST /legal/voice-query ...")
    try:
        with open(audio_path, "rb") as f:
            resp = requests.post(
                VOICE_URL,
                files={"file": (audio_path, f, "audio/mpeg")},
                data={"language": ""},
                timeout=120,
            )

        if resp.status_code == 200:
            data = resp.json()
            transcription = data.get("transcription", "N/A")
            answer_text   = data.get("answer_text", "N/A")
            audio_url     = data.get("audio_url", "N/A")
            sources       = data.get("sources", [])

            print(f"\n  [STATUS]  SUCCESS 200")
            print(f"  [TRANSCRIPTION]  {transcription}")
            print(f"  [ANSWER TEXT]    {answer_text[:300]}{'...' if len(answer_text)>300 else ''}")
            print(f"  [AUDIO URL]      {BASE_URL}{audio_url}")
            print(f"  [SOURCES COUNT]  {len(sources)} sources from KG/RAG")

            # Step 3: Verify audio file is accessible
            print(f"\n[3/3] Verifying audio URL is accessible...")
            try:
                audio_resp = requests.get(f"{BASE_URL}{audio_url}", timeout=10)
                if audio_resp.status_code == 200:
                    size_kb = len(audio_resp.content) / 1024
                    print(f"      AUDIO OK — {size_kb:.1f} KB MP3 downloaded successfully")
                else:
                    print(f"      AUDIO FAIL — HTTP {audio_resp.status_code}")
            except Exception as ae:
                print(f"      AUDIO check error: {ae}")
        else:
            print(f"  ERROR {resp.status_code}: {resp.text[:500]}")

    except requests.exceptions.ConnectionError:
        print("  CONNECTION ERROR — Is the backend running on port 8001?")
    except Exception as e:
        print(f"  REQUEST FAILED: {e}")
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)

    time.sleep(1)


if __name__ == "__main__":
    separator("VOICE PIPELINE END-TO-END TEST")
    print(f"Backend: {BASE_URL}")
    print(f"Total tests: {len(QUESTIONS)}\n")

    # Quick health check
    try:
        hc = requests.get(f"{BASE_URL}/docs", timeout=5)
        print(f"Backend reachable: YES (HTTP {hc.status_code})")
    except Exception:
        print("Backend NOT reachable — please start it with:")
        print("  venv\\Scripts\\python.exe -m uvicorn app.main:app --port 8001")
        sys.exit(1)

    for i, q in enumerate(QUESTIONS):
        run_test(i, q)

    separator("ALL TESTS COMPLETED")
