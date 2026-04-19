"""Research-grade audio mirror agent using Cactus + Gemma-4 (E2B).

This module implements a low-latency voice agent intended for research
experimentation with Gemma's audio reasoning. The agent detects the input
language from the audio signal and mirrors responses in the same language.

Run inside WSL2 with audio bridging (see `README.md`).
"""
import argparse
import signal
import sys
import time

import cactus_ai as cactus
import numpy as np
import pyaudio


RESEARCH_SYSTEM_PROMPT = """
You are an experimental low-latency audio agent used for research.
Detect the language from the user's raw audio and respond using the same
language. For Spanish audio, respond entirely in Spanish.
Be concise and avoid adding translations or meta-comments.
"""


def build_args():
    p = argparse.ArgumentParser(description="Audio Mirror Agent (research)")
    p.add_argument("--token", required=True, help="Cactus authentication token")
    p.add_argument("--model", default="google/gemma-4-E2B-it", help="Cactus model id")
    p.add_argument("--rate", type=int, default=16000, help="Audio sampling rate")
    p.add_argument("--frames", type=int, default=1024, help="Frames per audio buffer")
    return p.parse_args()


def start_agent(token: str, model_name: str, rate: int, frames: int):
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

    print("Audio Mirror Agent (research) active — press Ctrl+C to stop.")

    try:
        while running:
            try:
                raw = in_stream.read(frames, exception_on_overflow=False)
            except Exception:
                time.sleep(0.01)
                continue

            samples = np.frombuffer(raw, dtype=np.int16)

            stream_iter = model.generate(
                input_audio=samples,
                system_prompt=RESEARCH_SYSTEM_PROMPT,
                stream=True,
            )

            for pkt in stream_iter:
                if not pkt:
                    continue
                audio_bytes = getattr(pkt, "audio", None)
                if audio_bytes:
                    try:
                        out_stream.write(audio_bytes)
                    except Exception:
                        pass

    finally:
        try:
            in_stream.stop_stream(); in_stream.close()
        except Exception:
            pass
        try:
            out_stream.stop_stream(); out_stream.close()
        except Exception:
            pass
        pa.terminate()


if __name__ == "__main__":
    args = build_args()
    try:
        start_agent(args.token, args.model, args.rate, args.frames)
    except Exception as exc:
        print("Agent error:", exc)
        sys.exit(1)
