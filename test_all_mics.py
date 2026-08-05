"""Deep mic test — tries each device at its native sample rate."""
import pyaudio
import struct

CHUNK = 1024
RECORD_SECONDS = 3

p = pyaudio.PyAudio()

print("\n=== DEEP MIC TEST — SPEAK LOUDLY INTO YOUR MIC! ===\n")

for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if int(info.get("maxInputChannels", 0)) <= 0:
        continue

    name = info.get("name", "?")
    native_rate = int(info.get("defaultSampleRate", 44100))

    for rate in [native_rate, 44100, 16000, 48000]:
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=rate,
                input=True,
                input_device_index=i,
                frames_per_buffer=CHUNK,
            )
            frames = []
            for _ in range(int(rate / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            stream.stop_stream()
            stream.close()

            raw = b"".join(frames)
            nums = struct.unpack("<%dh" % (len(raw) // 2), raw)
            max_amp = max(abs(x) for x in nums) if nums else 0

            status = "*** WORKING ***" if max_amp > 500 else ("maybe" if max_amp > 50 else "silent")
            print(f"  [{i:2d}] {name:<50} rate={rate:5d}  amp={max_amp:6d}  {status}")
            break  # first working rate is enough
        except Exception:
            continue
    else:
        print(f"  [{i:2d}] {name:<50} ALL RATES FAILED")

p.terminate()

print("\n--- WINDOWS SETTINGS CHECK ---")
print("1. Right-click speaker icon in taskbar -> Sound Settings")
print("2. Go to 'Input' section")
print("3. Make sure your Microphone is selected and NOT muted")
print("4. Check the volume slider is above 50%")
print("5. Click 'Device properties' -> make sure 'Disable' is NOT checked")
print("6. Try speaking — the input level meter should move")
