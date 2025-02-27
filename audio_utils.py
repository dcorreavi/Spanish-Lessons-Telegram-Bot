from gtts import gTTS
import os
from pathlib import Path

def generate_audio(text: str, lang: str = 'es') -> str:
    """
    Generate audio file for the given text and return the file path
    """
    # Create audio directory if it doesn't exist
    audio_dir = Path("audio_files")
    audio_dir.mkdir(exist_ok=True)
    
    # Create a filename based on the text (simplified)
    filename = f"audio_{hash(text)}.mp3"
    filepath = audio_dir / filename
    
    # Generate audio file if it doesn't exist
    if not filepath.exists():
        tts = gTTS(text=text, lang=lang)
        tts.save(str(filepath))
    
    return str(filepath) 