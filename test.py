import soundfile as sf
import simpleaudio as sa
import socket
import array
import sys
from util import sendData, receiveData

HOST = "127.0.0.1"
PORT = 65432

if __name__ == '__main__':
  if len(sys.argv) <= 1:
    print(f"Usage: {sys.argv[0]} <file.wav>")
    sys.exit(-1)
  file = sys.argv[1]
  audio, sample_rate = sf.read(
    "bak/test_16k_mono.wav",
    dtype='float32'
  )
  print(f"Loaded audio file (rate={sample_rate}, len={len(audio)})")

  data = bytearray(audio)
  print("Converted to {} bytes of data".format(len(data)))

  print("Opening socket...")
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print("Connecting to server...")
    s.connect((HOST, PORT))
    print("Connected, sending data...")
    sendData(s, data)
    print("Data sent, waiting for reply...")
    data = receiveData(s)
    print(f"Received {len(data)} bytes of audio data.")
    print("Closing connection")
    s.close()
  
  audio = array.array('f', data).tolist()
  wave_obj = sa.WaveObject(
    data,
    num_channels=1,
    bytes_per_sample=4,
    sample_rate=16000
  )
  play_obj = wave_obj.play()
  play_obj.wait_done()

print("Press enter to quit.")
input()
