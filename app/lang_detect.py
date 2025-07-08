from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0 

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception as e:
        print(f"[LangDetect] Failed to detect language: {e}")
        return "en" 
