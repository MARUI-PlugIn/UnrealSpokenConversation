from TextResponse import TextResponse
from transformers import AutoTokenizer, AutoModelForCausalLM

class TextResponse_DialoGPT(TextResponse):
  def __init__(self):
    super().__init__()
    self.tokenizer = AutoTokenizer.from_pretrained(
      "microsoft/DialoGPT-small",
      cache_dir="./models/"
    )
    self.model = AutoModelForCausalLM.from_pretrained(
      "microsoft/DialoGPT-small",
      cache_dir="./models/"
    )

  def __call__(self, text):
    input_ids = self.tokenizer.encode(
      text + self.tokenizer.eos_token,
      return_tensors='pt'
    )
    chat_history_ids = self.model.generate(
      input_ids,
      max_length=1000,
      pad_token_id=self.tokenizer.eos_token_id
    )
    reply = self.tokenizer.decode(
      chat_history_ids[:, input_ids.shape[-1]:][0],
      skip_special_tokens=True
    )
    return reply
