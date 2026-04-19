"""Cactus + Gemma-4 voice-to-voice mirror agent (WSL2 on Windows).

Usage:
  python voice_agent.py --token YOUR_CACTUS_TOKEN

Notes:
 - Run inside WSL2 on Windows (see README.md for PulseAudio bridging).
 - Ensure you've run: `cactus download google/gemma-4-E2B-it`
"""
import argparse
import signal
import sys
import time

import cactus_ai as cactus
import numpy as np
import pyaudio


SYSTEM_PROMPT = """
You are a low-latency voice assistant.
Detect the language of the user's audio input.
Always respond in the EXACT same language used by the user.
If the user speaks Spanish, your response must be entirely in Spanish.
"""


def build_args():
    p = argparse.ArgumentParser()
    p.add_argument("--token", required=True, help="Cactus auth token")
    p.add_argument("--model", default="google/gemma-4-E2B-it", help="Cactus model id")
    p.add_argument("--rate", type=int, default=16000, help="Audio sample rate")
    p.add_argument("--frames", type=int, default=1024, help="Frames per buffer")
    return p.parse_args()


def start_voice_agent(token: str, model_name: str, rate: int, frames: int):
    cactus.auth(token=token)
    model = cactus.Model(model_name)

    pa = pyaudio.PyAudio()

    in_stream = pa.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=rate,
                        input=True,
                        frames_per_buffer=frames)

    out_stream = pa.open(format=pyaudio.paInt16,
                         channels=1,
                         rate=rate,
                         output=True,
                         frames_per_buffer=frames)

    running = True

    def _stop(signum, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    print("Cactus Voice Agent Active. Speak now (Ctrl+C to stop).")

    try:
        while running:
            try:
                data = in_stream.read(frames, exception_on_overflow=False)
            except Exception:
                # In case of occasional read issues, sleep briefly and continue
                time.sleep(0.01)
                continue

            audio_chunk = np.frombuffer(data, dtype=np.int16)

            # Pass raw audio to the model for direct audio reasoning / voice prompting
            # Gemma 4 (E2B) supports reasoning on the audio signal natively.
            response_stream = model.generate(
                input_audio=audio_chunk,
                system_prompt=SYSTEM_PROMPT,
                stream=True,
            )

            # Stream the returned audio to the speakers
            for chunk in response_stream:
                if not chunk:
                    continue
                # Some stream chunks may carry audio bytes under `.audio`
                audio_bytes = getattr(chunk, "audio", None)
                if audio_bytes:
                    try:
                        out_stream.write(audio_bytes)
                    except Exception:
                        # If output fails, continue (do not crash the loop)
                        pass

    finally:
        try:
            in_stream.stop_stream()
            in_stream.close()
        except Exception:
            pass
        try:
            out_stream.stop_stream()
            out_stream.close()
        except Exception:
            pass
        pa.terminate()


if __name__ == "__main__":
    args = build_args()
    try:
        start_voice_agent(args.token, args.model, args.rate, args.frames)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)
