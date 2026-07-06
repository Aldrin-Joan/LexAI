import whisper

# Load model once globally (Upgrading to 'small' for better multi-lingual accuracy)
model = whisper.load_model("small")

def transcribe_audio(file_path: str) -> str:
    result = model.transcribe(file_path, task="transcribe")
    return result["text"]