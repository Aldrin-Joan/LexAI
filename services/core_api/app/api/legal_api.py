from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import shutil
import uuid
from app.services.ai_service import AIService
from app.services.file_service import FileService
from app.services.translation_service import TranslationService
from app.services.voice.stt import transcribe_audio
from app.services.voice.tts import text_to_speech

router = APIRouter(prefix="/legal", tags=["legal"])


class ChatQuery(BaseModel):
    message: str


@router.post("/ai-chat")
async def ai_chat(query: ChatQuery):
    answer, sources = await AIService.get_legal_advice(query.message)
    return {"response": answer, "sources": sources, "type": "text"}


@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    allowed_extensions = ["pdf", "docx", "jpg", "jpeg", "png"]
    ext = file.filename.split(".")[-1].lower()

    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="File type not supported")

    content = await file.read()
    result = await FileService.process_document(content, file.filename)
    return result


@router.get("/lawyers")
async def get_lawyers():
    # Placeholder for lawyer discovery
    return [
        {
            "id": 1,
            "name": "Adv. Rajesh Kumar",
            "specialization": "Criminal Law",
            "rating": 4.8,
        },
        {
            "id": 2,
            "name": "Adv. Sneha Sharma",
            "specialization": "Corporate Law",
            "rating": 4.9,
        },
        {
            "id": 3,
            "name": "Adv. Anjali Menon",
            "specialization": "Family Law",
            "rating": 4.7,
        },
    ]


@router.post("/voice-query")
async def voice_query(file: UploadFile = File(...), language: str = Form(None)):
    if not file.filename.endswith((".wav", ".mp3", ".m4a", ".ogg", ".aac")):
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    # Ignore swagger's default value for string
    if language == "string":
        language = None

    # Save audio temporarily
    temp_dir = os.path.join(os.getcwd(), "backend", "data", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_audio_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
    
    with open(temp_audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Step 1: STT
        try:
            transcription = transcribe_audio(temp_audio_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"STT Error: {str(e)}")
        
        # Determine language for TTS. 
        translator = TranslationService()
        source_lang = language or translator.detect_language(transcription)

        # Restrict TTS Languages (Fix 3)
        supported_langs = ["en", "hi", "ta", "te", "kn", "ml", "bn", "es", "fr"]
        if source_lang not in supported_langs:
            source_lang = "en"

        # Step 2: Get Answer (AIService handles translation and RAG)
        answer_text, expanded_sources = await AIService.get_legal_advice(transcription)
        
        # Step 3: TTS
        audio_filename = f"response_{uuid.uuid4()}.mp3"
        audio_filepath = os.path.join(os.getcwd(), "backend", "data", "audio", audio_filename)
        os.makedirs(os.path.dirname(audio_filepath), exist_ok=True)
        
        # langdetect returns 'en', 'hi', etc which aligns well with gTTS
        output_path = text_to_speech(answer_text, lang=source_lang, output_path=audio_filepath)
        
        # Return response
        return {
            "transcription": transcription,
            "answer_text": answer_text,
            "audio_url": f"/legal/audio/{audio_filename}",
            "sources": expanded_sources
        }
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


@router.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(os.getcwd(), "backend", "data", "audio", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg")
    raise HTTPException(status_code=404, detail="Audio file not found")
