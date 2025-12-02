import asyncio
import base64

from app.app.services.openai_service import OpenAIService
from app.app.core.config import settings

"""
Voice Feature Test

This script performs a round‑trip test:
1. Generate speech from sample text (TTS)
2. Transcribe the generated audio back to text (STT)
3. Report basic metrics and similarity score

Run inside backend container:
  docker compose exec backend python test_voice_features.py
"""

SAMPLE_TEXT = "Hello, this is a Morgan State University Computer Science voice feature test."

async def main():
    service = OpenAIService()

    print("[TTS] Generating audio...")
    audio_bytes = await service.text_to_speech(SAMPLE_TEXT)
    print(f"[TTS] Audio bytes: {len(audio_bytes)}")

    # Optional: show a short base64 preview (first 60 bytes)
    preview_b64 = base64.b64encode(audio_bytes[:60]).decode()
    print(f"[TTS] Base64 preview: {preview_b64}...")

    print("[STT] Transcribing audio...")
    transcript = await service.speech_to_text(audio_bytes)
    print(f"[STT] Transcript: {transcript}")

    # Simple similarity metric
    original_lower = SAMPLE_TEXT.lower()
    transcript_lower = transcript.lower()
    common = sum(1 for w in original_lower.split() if w in transcript_lower)
    similarity = common / len(original_lower.split())
    print(f"[RESULT] Word overlap similarity: {similarity:.2f}")

    # Basic success heuristic
    if similarity > 0.6:
        print("[SUCCESS] Voice round-trip functioning within expected range.")
    else:
        print("[WARN] Similarity low; check audio format or model settings.")

if __name__ == "__main__":
    asyncio.run(main())
