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

    from config import VOSK_MODEL_PATH
    vosk.SetLogLevel(-1)
    model = vosk.Model(VOSK_MODEL_PATH)
    recognizer = vosk.KaldiRecognizer(model, 16000)

    print("Please say 'sam'...")
    start = time.time()
    
    while time.time() - start < 10: # run for 10 seconds
        raw_data = stream.read(4000, exception_on_overflow=False)
        count = len(raw_data) // (2 * channels)
        samples = struct.unpack(f"<{count * channels}h", raw_data[:count * 2 * channels])
        
        # Smart extraction
        best_ch = 0
        max_valid_energy = -1
        for ch in range(channels):
            ch_samples = samples[ch::channels]
            mean = sum(ch_samples) / count if count > 0 else 0
            ac_energy = max(abs(s - mean) for s in ch_samples)
            if 50 < ac_energy < 15000:
                if ac_energy > max_valid_energy:
                    max_valid_energy = ac_energy
                    best_ch = ch
        
        if max_valid_energy == -1:
            best_ch = 1 if channels >= 4 else 0
            
        mono_samples = samples[best_ch::channels]
        data = struct.pack(f"<{count}h", *mono_samples)
        
        is_phrase_complete = recognizer.AcceptWaveform(data)
        
        if is_phrase_complete:
            res = json.loads(recognizer.Result())
            text = res.get("text", "")
            print(f"[Vosk detected pause] Result: '{text}' (Channel used: {best_ch}, Energy: {max_valid_energy})")
        else:
            partial = json.loads(recognizer.PartialResult())
            ptext = partial.get("partial", "")
            if ptext:
                print(f"[Partial] '{ptext}'")

    stream.stop_stream()
    stream.close()

except Exception as e:
    print(f"Error: {e}")
finally:
    pa.terminate()
