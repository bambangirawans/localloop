from faster_whisper import WhisperModel
import tempfile

model = WhisperModel("base", compute_type="int8")  

def transcribe_audio(audio_file) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
        audio_file.save(tmp.name)
        segments, _ = model.transcribe(tmp.name)
        return " ".join([segment.text.strip() for segment in segments])