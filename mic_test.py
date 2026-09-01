import pyaudio
import time
import struct
import os

device_index = os.getenv("SAM_MICROPHONE_INDEX")
if device_index:
    device_index = int(device_index)

pa = pyaudio.PyAudio()

try:
    dev_info = pa.get_device_info_by_index(device_index) if device_index is not None else pa.get_default_input_device_info()
    print(f"Testing Mic: {dev_info.get('name')}")

    try:
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=4000,
        )
        print("Successfully opened in MONO (1 channel)")
    except Exception as e:
        print(f"Failed to open in MONO: {e}")
        stream = None

    if stream:
        print("Listening for 10 frames in MONO...")
        for i in range(10):
            data = stream.read(4000, exception_on_overflow=False)
            count = len(data) // 2
            samples = struct.unpack(f"<{count}h", data)
            amp = max(abs(s) for s in samples) if samples else 0
            print(f"Frame {i}: Amplitude = {amp}")
            time.sleep(0.1)
        stream.stop_stream()
        stream.close()

except Exception as e:
    print(f"Error: {e}")
finally:
    pa.terminate()
