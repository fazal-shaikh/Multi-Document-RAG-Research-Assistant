import os
import logging
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

# Initialize model once (singleton pattern)
_model = None

def get_model():
    global _model
    if _model is None:
        try:
            # Using "base" model as requested
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            _model = WhisperModel("base", device=device, compute_type="int8" if device == "cpu" else "float16")
            logger.info(f"Whisper model loaded successfully on {device}.")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            raise e
    return _model

def transcribe_audio(audio_path):
    """
    Transcribes audio file using faster-whisper.
    """
    try:
        model = get_model()
        segments, info = model.transcribe(audio_path, beam_size=5)
        
        transcript = ""
        for segment in segments:
            transcript += segment.text + " "
            
        return transcript.strip()
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return f"Error transcribing audio: {e}"
