import socket
import array
import time
import sys
from util import sendData, receiveData
from SpeechToText_wav2vec2Deutsch import SpeechToText_wav2vec2Deutsch
from SpeechToText_wav2vec2English import SpeechToText_wav2vec2English
from TextResponse_DialoGPT import TextResponse_DialoGPT
from TextResponse_germangpt2easy import TextResponse_germangpt2easy
from TextToSpeech_mmsttsDeutsch import TextToSpeech_mmsttsDeutsch
from TextToSpeech_mmsttsEnglish import TextToSpeech_mmsttsEnglish

HOST = "127.0.0.1"
PORT = 65432



def main() -> int:
  if len(sys.argv) <= 1:
    print(f"Usage: {sys.argv[0]} <de|en>")
    return -1
  language = sys.argv[1]
  if language == "en":
    speechToText = SpeechToText_wav2vec2English()
    textResponse = TextResponse_DialoGPT()
    textToSpeech = TextToSpeech_mmsttsEnglish()
  elif language == "de":
    speechToText = SpeechToText_wav2vec2Deutsch()
    textResponse = TextResponse_germangpt2easy()
    textToSpeech = TextToSpeech_mmsttsDeutsch()
  else:
    print(f"[ERROR] Unknown language {language}")
    print(f"Usage: {sys.argv[0]} <de|en>")
    return -1
  print(f"\nListening on {HOST}:{PORT}")
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(0.2)
    sock.bind((HOST, PORT))
    sock.listen()
    while True:
      try: 
        conn, addr = sock.accept() 
      except socket.timeout:
        continue
      conn.setblocking(False) 
      with conn:
        print(f"Connected to {addr}")
        while True:
          try:
            data = receiveData(conn)
          except:
            print("Disconnected.")
            break
          audio = array.array('f', data).tolist()
          text = speechToText(audio)
          print(F"> {text}")
          text = textResponse(text)
          print(F"< {text}")
          data = textToSpeech(text)
          sendData(conn, data)
  return 0

if __name__ == '__main__':
  sys.exit(main())
