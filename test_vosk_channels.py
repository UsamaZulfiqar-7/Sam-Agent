import pyaudio
import time
import struct
import os
import json
import vosk

device_index = os.getenv("SAM_MICROPHONE_INDEX")
if device_index:
    device_index = int(device_index)

pa = pyaudio.PyAudio()

try:
    dev_info = pa.get_device_info_by_index(device_index) if device_index is not None else pa.get_default_input_device_info()
    channels = int(dev_info.get("maxInputChannels", 1))
    print(f"Testing Mic: {dev_info.get('name')} (Channels: {channels})")

    stream = pa.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=16000,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=4000,
    )

    print("Please say 'hello sam' in the next 5 seconds...")
    frames = []
    for _ in range(50): # 5 seconds
        data = stream.read(4000, exception_on_overflow=False)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    
    print("Recording finished. Testing each channel with Vosk...")
    
    # Process each channel
    from config import VOSK_MODEL_PATH
    vosk.SetLogLevel(-1)
    model = vosk.Model(VOSK_MODEL_PATH)
    
    for ch in range(channels):
        recognizer = vosk.KaldiRecognizer(model, 16000)
        
        for raw_data in frames:
            count = len(raw_data) // (2 * channels)
            samples = struct.unpack(f"<{count * channels}h", raw_data[:count * 2 * channels])
            ch_samples = samples[ch::channels]
            data = struct.pack(f"<{count}h", *ch_samples)
            recognizer.AcceptWaveform(data)
            
        result = json.loads(recognizer.FinalResult())
        text = result.get("text", "")
        print(f"Channel {ch} recognized text: '{text}'")

except Exception as e:
    print(f"Error: {e}")
finally:
    pa.terminate()
