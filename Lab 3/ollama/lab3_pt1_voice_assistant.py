import os
import sounddevice as sd
import vosk
import queue
import sys
import json
import requests

# ---- Speech Recognition Setup ----
model = vosk.Model("vosk-model-small-en-us-0.15")
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

duration = 5
samplerate = 16000
with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    print("Please speak your input:")
    rec_text = ""
    for _ in range(int(duration * samplerate / 8000)):
        data = q.get()
        rec = vosk.KaldiRecognizer(model, samplerate)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            rec_text += result.get("text", "")
    print("Recognized:", rec_text)

# ---- Ollama Processing ----
ollama_api_url = "http://localhost:5000/process"
response = requests.post(ollama_api_url, json={"input": rec_text})
ollama_text = response.json().get("output", "I didn't understand that.")

print("Ollama says:", ollama_text)
os.system(f'espeak "{ollama_text}"')
