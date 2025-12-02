import asyncio
import base64
import httpx

URL = "http://localhost:8000"
SAMPLE_TEXT = "Morgan AI voice HTTP round trip test."  # keep short

async def main():
    async with httpx.AsyncClient(timeout=60) as client:
        # TTS
        tts_resp = await client.post(f"{URL}/api/voice/text-to-speech", json={
            "text": SAMPLE_TEXT,
            "voice": "alloy",
            "speed": 1.0,
            "format": "mp3"
        })
        tts_resp.raise_for_status()
        audio_bytes = tts_resp.content
        print(f"[HTTP TTS] Received {len(audio_bytes)} bytes")
        print(f"[HTTP TTS] Preview b64: {base64.b64encode(audio_bytes[:40]).decode()}...")

        # STT
        files = {"audio": ("sample.mp3", audio_bytes, "audio/mpeg")}
        stt_resp = await client.post(f"{URL}/api/voice/speech-to-text", files=files, data={"language": "en"})
        stt_resp.raise_for_status()
        stt_json = stt_resp.json()
        print(f"[HTTP STT] Transcript: {stt_json['text']}")

        # Simple similarity
        orig_words = SAMPLE_TEXT.lower().split()
        trans_lower = stt_json['text'].lower()
        overlap = sum(1 for w in orig_words if w in trans_lower)
        similarity = overlap / len(orig_words)
        print(f"[RESULT] Similarity: {similarity:.2f}")
        if similarity > 0.6:
            print("[SUCCESS] HTTP roundtrip functioning.")
        else:
            print("[WARN] Similarity low, investigate models or audio integrity.")

if __name__ == "__main__":
    asyncio.run(main())
