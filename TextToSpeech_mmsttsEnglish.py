from TextToSpeech import TextToSpeech
from transformers import VitsModel, AutoTokenizer
import torch

class TextToSpeech_mmsttsEnglish(TextToSpeech):
  def __init__(self):
    super().__init__()
    self.model = VitsModel.from_pretrained(
        "facebook/mms-tts-eng",
        cache_dir="./models/"
    )
    self.tokenizer = AutoTokenizer.from_pretrained(
        "facebook/mms-tts-eng",
        cache_dir="./models/"
    )

  def __call__(self, text):
    inputs = self.tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        audio = self.model(**inputs).waveform
    # sampling_rate = self.model.config.sampling_rate
    # print("Synthesized audio: rate={}, samples={}, sample[0]={}".format(sampling_rate, len(audio[0]), audio[0][0]))
    data = bytearray(audio[0].detach().cpu().numpy())
    return data
