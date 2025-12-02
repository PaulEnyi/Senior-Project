import asyncio
import base64

from app.services.openai_service import OpenAIService

SAMPLE_TEXT = "Hello, this is a Morgan State University Computer Science voice feature test."

async def main():
    service = OpenAIService()

    print("[TTS] Generating audio...")
    audio_bytes = await service.text_to_speech(SAMPLE_TEXT)
    print(f"[TTS] Audio bytes: {len(audio_bytes)}")
    print(f"[TTS] First 60 bytes (b64): {base64.b64encode(audio_bytes[:60]).decode()}...")

    print("[STT] Transcribing audio...")
    transcript = await service.speech_to_text(audio_bytes)
    print(f"[STT] Transcript: {transcript}")

    original_words = SAMPLE_TEXT.lower().split()
    transcribed_lower = transcript.lower()
    overlap = sum(1 for w in original_words if w in transcribed_lower)
    similarity = overlap / len(original_words)
    print(f"[RESULT] Word overlap similarity: {similarity:.2f}")

    if similarity > 0.6:
        print("[SUCCESS] Voice round-trip functioning.")
    else:
        print("[WARN] Similarity below threshold; check audio format or model availability.")

if __name__ == "__main__":
    asyncio.run(main())
