import cv2
import uuid
from typing import Optional
from database import get_db, User
import base64
import pyaudio
import numpy as np
import wave
import uuid
import base64


def capture_photo():
    # Open the camera and capture a single frame
    cap = cv2.VideoCapture(0)  # Use 0 for the default camera
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return "Failed to capture photo"

    # Save the image temporarily and return as base64
    img_path = f"{uuid.uuid4()}.png"
    cv2.imwrite(img_path, frame)

    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


async def record_voice():
    # Audio configuration
    CHUNK = 1024  # Buffer size
    FORMAT = pyaudio.paInt16  # 16-bit PCM
    CHANNELS = 1  # Mono
    RATE = 44100  # Sample rate
    RECORD_SECONDS = 5  # Record time
    WAVE_OUTPUT_FILENAME = f"{uuid.uuid4()}.wav"

    p = pyaudio.PyAudio()

    stream = p.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
    )

    print("Recording...")

    frames = []

    # Record in chunks for 5 seconds
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording complete.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the audio file
    wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()

    # Return the audio file as base64
    with open(WAVE_OUTPUT_FILENAME, "rb") as audio_file:
        return base64.b64encode(audio_file.read()).decode("utf-8")


def detect_cross_question(user_input):
    """Detects if the user's input is a cross-question."""
    cross_question_keywords = ["why", "reason", "purpose", "necessary", "mandatory"]
    return any(keyword in user_input.lower() for keyword in cross_question_keywords)


def handle_cross_question(field):
    """Returns a response to cross-questions."""
    responses = {
        "name": "Your name is necessary to register you correctly for the event.\n Let's start over. What is your name?",
        "gender": "We require gender information to ensure personalized experiences during the event. \n Please provide your gender.",
        "profile_picture": "A profile picture is necessary for identification at the event. Please provide a profile picture and say 'ready' when yu are ready.",
        "voice_sample": "The voice sample will be used to verify your identity. Please provide a voice sample and say 'ready' when you are ready.",
        "confirm_name": "Confirming your name helps us avoid registration errors.",
    }
    return responses.get(field, "This information is necessary for event registration.")
