from SpeechToText import SpeechToText
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch

class SpeechToText_wav2vec2English(SpeechToText):
  def __init__(self):
    super().__init__()
    self.processor = Wav2Vec2Processor.from_pretrained(
      "facebook/wav2vec2-base-960h",
      cache_dir="./models/"
    )
    self.model = Wav2Vec2ForCTC.from_pretrained(
      "facebook/wav2vec2-base-960h",
      cache_dir="./models/"
    )

  def __call__(self, audio):
    input_values = self.processor(
      audio,
      sampling_rate=16000,
      return_tensors="pt"
    ).input_values
    logits = self.model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = self.processor.decode(predicted_ids[0])
    return transcription
