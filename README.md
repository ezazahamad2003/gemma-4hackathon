# Cactus + Gemma-4 Voice Agent (Windows via WSL2)

This repository contains a minimal voice-to-voice agent using the Cactus Python SDK and Google Gemma 4 (E2B) that mirrors the user's spoken language (e.g., responds in Spanish when the user speaks Spanish).

Quick steps (high-level):

1. Install WSL2 and a Linux distro (Ubuntu recommended).
   - From Windows PowerShell (admin): `wsl --install`

2. Open your WSL2 distro and install Python and pip, then install dependencies:

```bash
python -m pip install --upgrade pip
pip install cactus-ai pyaudio numpy
# download the Gemma 4 model into the Cactus cache
cactus download google/gemma-4-E2B-it
```

3. Audio bridging (Windows -> WSL2):
- You need a PulseAudio server accessible from WSL. One common approach:
  - Install a Windows PulseAudio server (search for "PulseAudio for Windows" binaries).
  - In WSL, install client: `sudo apt install pulseaudio`
  - Configure the WSL PulseAudio client to point to the Windows PulseAudio server (set `default-server` in `/etc/pulse/client.conf` to the Windows host IP).

Notes: audio bridging setup can vary across Windows versions. If you prefer, test and debug audio with simple PyAudio scripts inside WSL first.

4. Run the agent:

```bash
python voice_agent.py --token YOUR_CACTUS_TOKEN
```

Replace `YOUR_CACTUS_TOKEN` with your Cactus API token.

If you need help setting up WSL2 audio routing or running the script, I can walk through the specific steps for your system.
