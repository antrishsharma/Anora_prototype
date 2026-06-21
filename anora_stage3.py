import pyautogui
import subprocess
import whisper
import sounddevice as sd
import numpy as np
import pyttsx3
import os
import base64
from groq import Groq
import threading
import time
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import cv2

# Setup — API key ab environment variable se aayegi, kabhi hardcode mat karna
# Windows pe set karne ke liye CMD mein: setx GROQ_API_KEY "tera-naya-key"
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
whisper_model = whisper.load_model("base")

SYSTEM_PROMPT = """You are Anora, a smart AI assistant created by Antrish Sharma. You can control the PC. Keep answers short and conversational."""

conversation = [{"role": "system", "content": SYSTEM_PROMPT}]

# ── PC Control Functions ──
def open_chrome():
    subprocess.Popen(['start', 'chrome', '--profile-directory=Default'], shell=True)
    time.sleep(3)

def open_youtube():
    subprocess.Popen(['start', 'chrome', 'https://www.youtube.com'], shell=True)
    time.sleep(3)

def open_notepad():
    subprocess.Popen(['notepad'], shell=True)
    time.sleep(1)

def take_screenshot():
    screenshot = pyautogui.screenshot()
    path = 'C:/Users/antrish sharma/OneDrive/Desktop/anora_ss.png'
    screenshot.save(path)

def get_volume_interface():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))

def volume_up():
    volume = get_volume_interface()
    current = volume.GetMasterVolumeLevelScalar()
    new_vol = min(1.0, current + 0.2)
    volume.SetMasterVolumeLevelScalar(new_vol, None)

def volume_down():
    volume = get_volume_interface()
    current = volume.GetMasterVolumeLevelScalar()
    new_vol = max(0.0, current - 0.2)
    volume.SetMasterVolumeLevelScalar(new_vol, None)

def volume_mute():
    volume = get_volume_interface()
    current = volume.GetMute()
    volume.SetMute(not current, None)

# ── Vision: camera ka latest frame yahan store hota hai ──
camera_running = False
camera_thread_ref = None
latest_frame = None
frame_lock = threading.Lock()

def camera_loop():
    global camera_running, latest_frame
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    camera_running = True
    while camera_running:
        ret, frame = cap.read()
        if not ret:
            break

        # har frame latest_frame mein save karo — vision query isi se uthayegi
        with frame_lock:
            latest_frame = frame.copy()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.imshow('Anora Vision', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            camera_running = False
            break
    cap.release()
    cv2.destroyAllWindows()

def open_camera():
    global camera_thread_ref
    camera_thread_ref = threading.Thread(target=camera_loop)
    camera_thread_ref.start()

def close_camera():
    global camera_running, latest_frame
    camera_running = False
    latest_frame = None

def describe_scene():
    """Camera ka latest frame Groq vision model ko bhejta hai aur real description leta hai."""
    with frame_lock:
        if latest_frame is None:
            return "Camera abhi khula nahi hai, pehle 'camera kholo' bol."
        frame = latest_frame.copy()

    success, buffer = cv2.imencode('.jpg', frame)
    if not success:
        return "Frame capture nahi ho paya, dobara try kar."

    img_base64 = base64.b64encode(buffer).decode('utf-8')

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Tum Anora ho. Is image mein jo dikh raha hai use 1-2 short sentences mein, jaise tum khud dekh rahi ho, casual Hinglish mein bata do."
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                    }
                ]
            }
        ]
    )
    return response.choices[0].message.content

# ── Command Detector ──
def detect_command(text):
    text = text.lower()
    if any(word in text for word in ["chrome kholo", "open chrome", "chrome open"]):
        open_chrome()
        return "Chrome khol diya!"
    elif any(word in text for word in ["youtube", "you tube"]):
        open_youtube()
        return "YouTube khol diya!"
    elif any(word in text for word in ["notepad", "note pad"]):
        open_notepad()
        return "Notepad khol diya!"
    elif any(word in text for word in ["screenshot", "screen shot", "screen capture"]):
        take_screenshot()
        return "Screenshot le liya Desktop pe save ho gaya!"
    elif any(word in text for word in ["volume up", "volume badha", "louder", "awaaz badha"]):
        volume_up()
        return "Volume badha diya!"
    elif any(word in text for word in ["volume down", "volume kam", "quieter", "awaaz kam"]):
        volume_down()
        return "Volume kam kar diya!"
    elif any(word in text for word in ["mute", "chup", "band karo awaaz"]):
        volume_mute()
        return "Mute kar diya!"
    elif any(word in text for word in ["camera kholo", "open camera", "camera on", "camera start"]):
        open_camera()
        return "Camera khol diya!"
    elif any(word in text for word in ["camera band", "close camera", "camera off"]):
        close_camera()
        return "Camera band kar diya!"
    elif any(word in text for word in ["see", "seeing", "dikh", "nazar", "what's in front", "background mein"]):
        return describe_scene()
    return None

# ── Voice Functions ──
def speak(text):
    print(f"Anora: {text}")
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()
    engine.stop()
    del engine

def listen():
    duration = 5
    samplerate = 16000
    print("Sun rahi hoon...")
    time.sleep(0.5)
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()
    audio = np.squeeze(audio)
    result = whisper_model.transcribe(audio, fp16=False, language="en")
    return result["text"].strip()

def think(user_text):
    conversation.append({"role": "user", "content": user_text})
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=conversation
    )
    reply = response.choices[0].message.content
    conversation.append({"role": "assistant", "content": reply})
    return reply

# ── Main Loop ──
print("ANORA Stage 3")
speak("Namaste Antrish!")

while True:
    user_text = listen()
    if not user_text:
        continue
    print(f"Tu: {user_text}")
    if "bye" in user_text.lower():
        speak("Theek hai, milte hain!")
        break
    command_result = detect_command(user_text)
    if command_result:
        speak(command_result)
    else:
        reply = think(user_text)
        speak(reply)
