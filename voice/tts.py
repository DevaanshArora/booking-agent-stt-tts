import os
import sounddevice as sd
import soundfile as sf
from openai import OpenAI

class TTSProvider:
    def __init__(self):
        self.client = OpenAI()
        self.filename = "output.wav"

    def speak(self, text: str):
        """
        Converts text to speech using OpenAI API and plays it.
        """
        print(f"Agent: {text}")
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text,
                response_format="wav"
            )
            
            # Save to file
            response.stream_to_file(self.filename)
            
            # Play audio
            data, fs = sf.read(self.filename)
            sd.play(data, fs)
            sd.wait()
            
        except Exception as e:
            print(f"Error during TTS: {e}")
