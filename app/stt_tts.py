# app/stt_tts.py
import os
from whisper import load_model   # from openai-whisper
from gtts import gTTS
from pathlib import Path
import tempfile

# load whisper small or base
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
WHISPER = load_model(WHISPER_MODEL)

def transcribe_audio_file(path: str) -> str:
    # whisper returns dict with 'text'
    res = WHISPER.transcribe(path)
    return res["text"]

def text_to_speech(text: str, filename: str = None) -> str:
    """
    Returns path to mp3 file created by gTTS
    """
    if filename is None:
        fd = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        filename = fd.name
        fd.close()
    tts = gTTS(text)
    tts.save(filename)
    return filename