from pathlib import Path


import asyncio

def generate_edge_tts(text: str, out_path: Path, voice: str = "en-US-GuyNeural"): 
    print(f"Generating {out_path.name} with edge-tts (voice={voice})")
    try:
        import edge_tts
    except Exception as e:
        print("edge-tts is not installed. Please run: python -m pip install edge-tts")
        raise
    async def run():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(out_path))
    asyncio.run(run())
#!/usr/bin/env python3
"""Simple TTS generator for the project.

This script uses gTTS to generate a couple of sample MP3 files and writes
them into the FrontEnd public assets audio folder so the frontend has
sample voices available.

Usage:
  python generate_tts.py

The script will create the directory if it doesn't exist and write two files:
  - morgan_clear.mp3
  - morgan_slow.mp3
"""
from pathlib import Path
import sys

try:
    from gtts import gTTS
except Exception as e:
    print("gTTS is not installed. Please run: python -m pip install gTTS")
    raise


def get_audio_dir() -> Path:
    # Repo root is three parents up from this script: scripts -> app -> BackEnd -> repo root
    repo_root = Path(__file__).resolve().parents[3]
    audio_dir = repo_root / "FrontEnd" / "public" / "assets" / "audio"
    return audio_dir


def generate(text: str, out_path: Path, lang: str = "en", slow: bool = False):
    print(f"Generating {out_path.name} (lang={lang}, slow={slow})")
    tts = gTTS(text=text, lang=lang, slow=slow)
    tts.save(str(out_path))


def main():
    audio_dir = get_audio_dir()
    audio_dir.mkdir(parents=True, exist_ok=True)

    samples = [
        # English clear
        (
            "Hello, this is Morgan AI. This is a clear example voice for the UI.",
            "morgan_clear.mp3",
            "en",
            False,
        ),
        # English slow
        (
            "Hello, this is Morgan AI speaking more slowly to improve clarity.",
            "morgan_slow.mp3",
            "en",
            True,
        ),
        # Spanish
        (
            "Hola, soy Morgan AI. Este es un ejemplo de voz en español.",
            "morgan_spanish.mp3",
            "es",
            False,
        ),
        # French
        (
            "Bonjour, je suis Morgan AI. Ceci est un exemple de voix en français.",
            "morgan_french.mp3",
            "fr",
            False,
        ),
        # English extra slow
        (
            "Hello, this is Morgan AI. Speaking very slowly for accessibility.",
            "morgan_very_slow.mp3",
            "en",
            True,
        ),
    ]

    created = []
    for sample in samples:
        text, fname, lang, slow = sample
        out = audio_dir / fname
        generate(text, out, lang=lang, slow=slow)
        created.append(out)

    print("Created files:")
    for p in created:
        print(" -", p)

    # Now generate a male voice sample using edge-tts
    male_voice_path = audio_dir / "morgan_male.mp3"
    try:
        generate_edge_tts(
            "Hello, this is Morgan AI with a male voice.",
            male_voice_path,
            voice="en-US-GuyNeural"
        )
        print("Created male voice file:", male_voice_path)
    except Exception as exc:
        print("Error generating male voice with edge-tts:", exc)
    audio_dir = get_audio_dir()
    audio_dir.mkdir(parents=True, exist_ok=True)


    samples = [
        # English clear
        (
            "Hello, this is Morgan AI. This is a clear example voice for the UI.",
            "morgan_clear.mp3",
            "en",
            False,
        ),
        # English slow
        (
            "Hello, this is Morgan AI speaking more slowly to improve clarity.",
            "morgan_slow.mp3",
            "en",
            True,
        ),
        # Spanish
        (
            "Hola, soy Morgan AI. Este es un ejemplo de voz en español.",
            "morgan_spanish.mp3",
            "es",
            False,
        ),
        # French
        (
            "Bonjour, je suis Morgan AI. Ceci est un exemple de voix en français.",
            "morgan_french.mp3",
            "fr",
            False,
        ),
        # English extra slow
        (
            "Hello, this is Morgan AI. Speaking very slowly for accessibility.",
            "morgan_very_slow.mp3",
            "en",
            True,
        ),
    ]


    created = []
    for sample in samples:
        text, fname, lang, slow = sample
        out = audio_dir / fname
        generate(text, out, lang=lang, slow=slow)
        created.append(out)

    print("Created files:")
    for p in created:
        print(" -", p)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("Error generating TTS:", exc)
        sys.exit(1)
