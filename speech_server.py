import socket
import array
import torch
import time
import numpy as np
from transformers import pipeline, Wav2Vec2ForCTC, Wav2Vec2Processor
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import VitsModel, AutoTokenizer


HOST = "127.0.0.1"
PORT = 65432


print("Initializing models...")

# For speech-to-text
# wav2vac_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h", cache_dir="./models/")
# wav2vac_model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h", cache_dir="./models/")
wav2vac_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-xlsr-53-german", cache_dir="./models/")
wav2vac_model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-xlsr-53-german", cache_dir="./models/")

# For text generation
# dialo_tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small", cache_dir="./models/")
# dialo_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small", cache_dir="./models/")
generator = pipeline('text-generation', model = "josh-oo/german-gpt2-easy")

# For text-to-speech
# synthesizer = pipeline("text-to-speech", "suno/bark-small")
tts_model = VitsModel.from_pretrained("facebook/mms-tts-deu", cache_dir="./models/")
tts_tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-deu", cache_dir="./models/")


recv_data_size = 116656 # 642740 # <- mono 16k 32bit 1285480 # <- mono 16k 64bit, 2570960 <- stereo 16k, 7712864 <- stereo 48k

print("\nOpening socket...")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("\nWaiting for connection...")
    conn, addr = s.accept()
    conn.setblocking(False) 
    with conn:
        print(f"Connected to {addr}")
        while True:
            print("\n\n# Waiting for input...")
            data = bytearray()
            while len(data) < 4:
                try:
                    packet = conn.recv(4 - len(data))
                except:
                    time.sleep(0.01)
                    continue
                data.extend(packet)
                
            recv_data_size = int.from_bytes(data, byteorder='little')
            print("Receiving {} bytes of audio...".format(recv_data_size))
            data = bytearray()
            while len(data) < recv_data_size:
                try:
                    packet = conn.recv(recv_data_size - len(data))
                except:
                    time.sleep(0.01)
                    continue
                data.extend(packet)
            # print("Received {} bytes of audio".format(len(data)))
            audio = array.array('f', data).tolist()
            # audio = np.reshape(audio, (2, -1)) # stereo [[l,r],[l,r],...]
            # print("First data samples: {}, {}, {}".format(audio[0], audio[1], audio[2]))
            
            input_values = wav2vac_processor(audio, sampling_rate=16000, return_tensors="pt").input_values
            logits = wav2vac_model(input_values).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = wav2vac_processor.decode(predicted_ids[0])
            print("Audio transcription: '{}'".format(transcription))
            
            # print("Tokenizing transcription...")
            # input_ids = dialo_tokenizer.encode(transcription + dialo_tokenizer.eos_token, return_tensors='pt')
            # chat_history_ids = dialo_model.generate(input_ids, max_length=1000, pad_token_id=dialo_tokenizer.eos_token_id)
            # transcription = dialo_tokenizer.decode(chat_history_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
            transcription = generator(transcription, max_length = 30, num_return_sequences=1)[0]['generated_text']
            print("Response: {}".format(transcription))
            
            tts_inputs = tts_tokenizer(transcription, return_tensors="pt")
            with torch.no_grad():
                audio = tts_model(**tts_inputs).waveform
            sampling_rate = tts_model.config.sampling_rate
            # print("Synthesized audio: rate={}, samples={}, sample[0]={}".format(sampling_rate, len(audio[0]), audio[0][0]))
            data = bytearray(audio[0].detach().cpu().numpy())
            send_data_size = len(data)
            print("Sending {} bytes of audio...".format(send_data_size))
            data_len = send_data_size.to_bytes(4, "little")
            conn.sendall(data_len)
            conn.sendall(data)

input()