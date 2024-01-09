from TextResponse import TextResponse
from transformers import pipeline

class TextResponse_germangpt2easy(TextResponse):
  def __init__(self):
    super().__init__()
    self.generator = pipeline(
      'text-generation',
      model = "josh-oo/german-gpt2-easy"
    )

  def __call__(self, text):
    reply = self.generator(
      text,
      max_length = 30,
      num_return_sequences=1
    )[0]['generated_text']
    return reply
