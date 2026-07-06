from app.services.voice.stt import transcribe_audio

text = transcribe_audio("sample.wav")
print("Transcription:", text)