# Anora — Personal AI Voice Assistant

Anora is a voice-controlled AI assistant built from scratch as a learning project, combining speech recognition, conversational reasoning, computer vision, and PC automation into one system. Inspired by Jarvis (Iron Man), the long-term goal is to evolve Anora into a physical robot.

Built by a first-year CSE student on an 8GB RAM laptop — every architectural decision (cloud APIs over local models, lightweight libraries, threaded camera capture) was made to work within that hardware constraint.

## Features

- **Conversational brain** — powered by Groq's LLM API for fast, low-latency responses
- **Voice input/output** — real-time speech-to-text (OpenAI Whisper) and text-to-speech (pyttsx3)
- **Computer vision** — live face detection via OpenCV, plus real scene description using a vision-language model (Anora can describe what's actually in front of the camera, not just detect a face)
- **PC automation** — opens applications (Chrome, YouTube, Notepad), takes screenshots, and controls system volume via voice commands

## Tech Stack

| Component | Tool |
|---|---|
| Reasoning | Groq API (LLM + vision model) |
| Speech-to-text | OpenAI Whisper |
| Text-to-speech | pyttsx3 |
| Vision | OpenCV (Haar Cascade) + Groq vision model |
| PC control | pyautogui, pycaw, subprocess |

## Project Stages

- **Stage 1 — Brain:** Conversational reasoning via Groq LLM
- **Stage 2 — Voice + Vision:** Speech I/O and live face detection
- **Stage 3 — PC Automation:** App control, volume control, real-time scene description (in progress)
- **Stage 4 (planned):** Physical robot body (Raspberry Pi/Arduino)

## Setup

1. Clone the repo and install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Get a free API key from [Groq](https://console.groq.com)
3. Set it as an environment variable (never hardcode it):
   ```
   setx GROQ_API_KEY "your-key-here"
   ```
4. Restart your terminal, then run:
   ```
   python anora_stage3.py
   ```

## Known Limitations

This is an active learning project — current limitations include response latency on lower-end hardware, and a few PC-automation commands still being refined. See commit history for active fixes.

## Author

Antrish Sharma — B.Tech CSE, Model Institute of Engineering & Technology, Jammu
