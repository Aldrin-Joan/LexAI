from gtts import gTTS
import os

def text_to_speech(text: str, lang: str = "hi", output_path: str = "output.mp3") -> str:
    """
    Converts text to speech and saves it as an MP3 file.
    
    Args:
        text: The text to convert to speech.
        lang: Language code (e.g., 'hi' for Hindi, 'en' for English).
        output_path: Where to save the generated audio.
        
    Returns:
        The path to the generated audio file.
    """
    try:
        tts = gTTS(text=text, lang=lang)
    except ValueError:
        # Fallback to English if the language code is not supported by gTTS
        print(f"Warning: Language '{lang}' not supported by gTTS. Falling back to English pronunciation.")
        tts = gTTS(text=text, lang="en")
        
    tts.save(output_path)
    return output_path
