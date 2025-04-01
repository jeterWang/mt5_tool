import wave
import math
import struct

# 创建WAV文件
sampleRate = 44100  # 采样率
duration = 0.1      # 持续时间（秒）
frequency = 1000    # 频率（Hz）

# 创建WAV文件
wav_file = wave.open("beep.wav", "w")
wav_file.setnchannels(1)        # 单声道
wav_file.setsampwidth(2)        # 2字节采样宽度
wav_file.setframerate(sampleRate)

# 生成正弦波
for i in range(int(duration * sampleRate)):
    value = int(32767 * math.sin(2 * math.pi * frequency * i / sampleRate))
    data = struct.pack('<h', value)
    wav_file.writeframes(data)

wav_file.close() 