import os
import sounddevice as sd
import soundfile as sf
import numpy as np
from openai import OpenAI

class STTProvider:
    def __init__(self):
        self.client = OpenAI()
        self.sample_rate = 44100
        self.channels = 1
        self.duration = 5  # Fixed duration for simplicity, or implement silence detection
        self.filename = "input.wav"

    def listen(self, prompt: str = "Listening...") -> str:
        """
        Records audio and transcribes it using OpenAI Whisper.
        """
        print(f"\n[{prompt}] (Recording for {self.duration}s...)")
        
        try:
            # Record audio
            recording = sd.rec(
                int(self.duration * self.sample_rate), 
                samplerate=self.sample_rate, 
                channels=self.channels,
                dtype='float32'
            )
            sd.wait()  # Wait until recording is finished
            
            # Save to file
            sf.write(self.filename, recording, self.sample_rate)
            print("Processing speech...")

            # Transcribe
            with open(self.filename, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file,
                    language="en"
                )
            
            text = transcription.text
            print(f"You said: {text}")
            return text

        except Exception as e:
            print(f"Error during STT: {e}")
            # Fallback to text input if audio fails
            return input(">> ").strip()
