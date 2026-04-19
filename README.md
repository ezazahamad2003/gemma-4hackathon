# Research Guide — Cactus + Gemma 4 Audio Mirror

This repository demonstrates an experimental, low-latency voice agent that uses the Cactus runtime with Google Gemma 4 (E2B) to reason directly over audio and mirror the user's spoken language (for example, respond in Spanish when the user speaks Spanish).

This README covers:
- High-level architecture and rationale
- How to install and run the agent inside WSL2 on Windows
- Audio bridging (PulseAudio) so your microphone and speakers work inside WSL2
- How to run the synthetic corpus generator for stress-testing
- Troubleshooting, privacy, and research notes

Contents in this repo (key files):
- `audio_mirror_agent.py` — research-grade voice agent that streams mic audio to Gemma and plays back audio responses.
- `project_generator.py` — synthetic corpus / project generator for creating large multi-file corpora for stress tests.
- `research_scaffold/` — small signal/audio utility modules used for experiments.
- `requirements.txt` — Python dependencies for quick installs.

Important: Cactus's local build and optimized libraries are Linux-oriented. On Windows you should run this project inside WSL2 (Windows Subsystem for Linux) to build and run Cactus correctly.

----

## 1) Architecture & Rationale

- Cactus (Python SDK) manages the local runtime, model loading, and optimized inference libraries.
- Gemma 4 (google/gemma-4-E2B-it) is used in its audio-capable variant (E2B). It reasons directly on raw audio input (the audio conformer + decoder) which allows a single-step audio→response pipeline without an explicit STT translation step.
- We use a short system prompt to instruct the model to "mirror" the language of the speaker at inference time.

This design minimizes latency and keeps the pipeline simple and reproducible for research.

----

## 2) Quick prerequisites (WSL2)

On Windows:

1. Install WSL2 and a Linux distro (Ubuntu recommended):

```powershell
wsl --install
```

2. Launch your WSL distro and update packages:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-venv python3-pip -y
```

3. (Optional) Create a virtualenv inside WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

4. Install Python dependencies inside WSL:

```bash
pip install -r /mnt/c/Users/ezaza/OneDrive/Desktop/gemma-4hackathon/requirements.txt
```

5. Download the model with Cactus (inside WSL):

```bash
# run once to populate the local cache
cactus download google/gemma-4-E2B-it
```

Note: If `cactus` is not found after `pip install cactus-ai`, ensure the Python environment used for `pip` is the one your shell sees (activate venv if you created one).

----

## 3) PulseAudio (Windows host) → WSL2 audio bridging

Because Cactus inference will run in WSL2, you must bridge audio devices so microphone input and speaker output are available to the Python process running inside WSL.

Minimal, tested approach:

1. Install a Windows PulseAudio server (for example, download a prebuilt `pulseaudio` binary for Windows). Run it on Windows and allow network access.

2. Find your Windows host IP from WSL (usually on WSL2 `grep nameserver /etc/resolv.conf` or use `cat /etc/resolv.conf` to find the `nameserver` entry — that's the Windows host IP from WSL's perspective).

3. In WSL, install the client and configure it to point to the Windows server:

```bash
sudo apt install pulseaudio -y
mkdir -p ~/.config/pulse
echo "default-server = tcp:<WINDOWS_HOST_IP>:4713" > ~/.config/pulse/client.conf
export PULSE_SERVER=tcp:<WINDOWS_HOST_IP>:4713
```

4. Start PulseAudio on Windows and verify you can list sinks/inputs from WSL using `pactl` (install `pulseaudio-utils` if needed):

```bash
pactl info
pactl list short sinks
```

5. Once the bridge works, PyAudio (inside WSL) can open the default input and output devices and the agent can read/write audio.

If you prefer, you can also use `pipewire` + `wireplumber` or other bridge tools; PulseAudio is widely compatible and easier for quick validation.

----

## 4) Running the research audio agent (inside WSL)

1. Ensure the model is downloaded (`cactus download ...`) and your `PULSE_SERVER` is set as described above.

2. Run the agent (from the repository root inside WSL):

```bash
python audio_mirror_agent.py --token YOUR_CACTUS_TOKEN
```

Replace `YOUR_CACTUS_TOKEN` with your Cactus auth token.

Behavior: the process captures microphone frames, sends them to the Cactus `Model.generate` API using the `input_audio` parameter and the research system prompt, and streams the audio response to your speaker.

Notes:
- Use `--rate` and `--frames` to tune latency vs. chunk size (defaults are 16 kHz and 1024 frames).
- If you encounter `ALSA`/device errors, confirm PulseAudio is reachable and that the WSL user can access the sound device via the bridge.

----

## 5) Running the synthetic corpus generator (option A)

If you need a large corpus for testing (this will use significant disk and time):

```bash
python project_generator.py --lines 1981000 --files 200 --out synthetic_corpus
```

- `--lines` controls the total number of placeholder lines produced.
- `--files` controls the number of files distributed across the corpus.

Warning: generating millions of lines can consume multiple GBs of storage and may take a long time depending on disk speed. For quick tests, try smaller numbers like `--lines 20000 --files 20`.

----

## 6) Troubleshooting

- If `cactus` commands fail: verify you installed `cactus-ai` in the same Python environment and that the executable is on your PATH inside WSL.
- If audio is silent or `pyaudio` fails to open a device: verify `PULSE_SERVER` and that the Windows PulseAudio server is running and not blocked by firewall.
- If the model doesn't generate audio chunks: confirm you downloaded the audio-capable Gemma E2B model and are using `input_audio=` with raw PCM samples.

----

## 7) Research notes and reproducibility

- System prompt: keep your prompt concise and prescriptive (see `RESEARCH_SYSTEM_PROMPT` in `audio_mirror_agent.py`). This helps the model behave predictably across runs.
- Model versioning: record the Cactus SDK version and the exact model id (`google/gemma-4-E2B-it`) used during experiments for reproducibility.
- Privacy: audio is processed locally; ensure you comply with any institutional / participant consent requirements before recording speech.

----

## 8) Next steps I can do for you

- (A) Run the synthetic corpus generator here (I will run `project_generator.py` to create the corpus). Note: this will use significant disk/time — say `yes` to proceed and specify `--lines`/`--files` if you want a specific size.
- (B) Walk you through step-by-step, interactive WSL2 + PulseAudio setup on your machine and then run `audio_mirror_agent.py` together. I can provide the exact commands and firewall settings to open for the PulseAudio server.

Tell me which option you want (A or B) and I will proceed.


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
