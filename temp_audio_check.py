import pyaudio
import struct

CHUNK = 1024
RATE = 44100
RECORD_SECONDS = 2

p = pyaudio.PyAudio()
print('Available devices:')
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info.get('maxInputChannels', 0) > 0:
        print(i, info.get('name'))

stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
print('Recording...')
frames = []
for _ in range(int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK, exception_on_overflow=False)
    frames.append(data)
stream.stop_stream()
stream.close()
p.terminate()
raw = b''.join(frames)
nums = struct.unpack('<%dh' % (len(raw) // 2), raw)
max_amp = max(abs(x) for x in nums) if nums else 0
print('max amplitude:', max_amp)