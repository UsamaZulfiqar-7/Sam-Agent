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
    channels = int(dev_info.get("maxInputChannels", 1))
    print(f"Diagnostics for Mic: {dev_info.get('name')} (Channels: {channels})")

    stream = pa.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=16000,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=4000,
    )

    print("Speak now for 3 seconds...")
    frames = []
    for _ in range(30):
        data = stream.read(4000, exception_on_overflow=False)
        frames.append(data)
    stream.stop_stream()
    stream.close()

    print("Analyzing channels...")
    for ch in range(channels):
        dc_offsets = []
        ac_amps = []
        for raw_data in frames:
            count = len(raw_data) // (2 * channels)
            samples = struct.unpack(f"<{count * channels}h", raw_data[:count * 2 * channels])
            ch_samples = samples[ch::channels]
            mean = sum(ch_samples) / count if count > 0 else 0
            ac = max(abs(s - mean) for s in ch_samples) if count > 0 else 0
            dc_offsets.append(abs(mean))
            ac_amps.append(ac)
        
        avg_dc = sum(dc_offsets) / len(dc_offsets)
        avg_ac = sum(ac_amps) / len(ac_amps)
        print(f"Channel {ch}: Avg DC Offset = {avg_dc:.1f}, Avg AC Energy = {avg_ac:.1f}")

except Exception as e:
    print(f"Error: {e}")
finally:
    pa.terminate()
