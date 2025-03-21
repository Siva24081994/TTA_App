from gtts import gTTS
import os
import hashlib

AUDIO_DIR = "static/audio"  # Store audio files persistently

# Ensure the directory exists
os.makedirs(AUDIO_DIR, exist_ok=True)

def generate_hindi_tts(text):
    """Generate Hindi TTS audio and save it persistently."""
    if not text.strip():
        raise ValueError("Error: Empty text provided for TTS!")

    # Generate a unique filename using SHA-1 (more stable than `hash()`)
    filename = hashlib.sha1(text.encode()).hexdigest()[:10] + ".mp3"
    file_path = os.path.join(AUDIO_DIR, filename)

    # Check if the file already exists (avoid regenerating)
    if not os.path.exists(file_path):
        try:
            tts = gTTS(text, lang="hi")
            tts.save(file_path)
            print(f"✅ TTS saved at: {file_path}")
        except Exception as e:
            print(f"❌ Error generating Hindi TTS: {e}")
            raise

    return os.path.abspath(file_path)  # Return absolute path
