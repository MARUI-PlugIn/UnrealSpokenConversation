from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import TrainingArguments
from transformers import Trainer
import numpy as np
from datasets import load_metric

training_args = TrainingArguments("test_trainer")
training_args.output_dir = "./training/"
training_args.per_device_train_batch_size = 8 # per CPU/GPU/TPU
training_args.logging_first_step = True

raw_datasets = load_dataset("imdb", cache_dir="./data/")
tokenizer = AutoTokenizer.from_pretrained(
  "microsoft/DialoGPT-small",
  cache_dir="./models/"
)
tokenizer.pad_token = tokenizer.eos_token

def tokenize_function(examples):
  return tokenizer(examples["text"], padding="max_length", truncation=True)

tokenized_datasets = raw_datasets.map(tokenize_function, batched=True)
small_train_dataset = tokenized_datasets["train"].shuffle(seed=23).select(range(1000)) 
small_eval_dataset = tokenized_datasets["test"].shuffle(seed=23).select(range(1000)) 
full_train_dataset = tokenized_datasets["train"]
full_eval_dataset = tokenized_datasets["test"]

model = AutoModelForCausalLM.from_pretrained(
  "microsoft/DialoGPT-small",
  cache_dir="./models/"
)

metric = load_metric("accuracy")
def compute_metrics(eval_pred):
  logits, labels = eval_pred
  predictions = np.argmax(logits, axis=-1)
  return metric.compute(predictions=predictions, references=labels)

trainer = Trainer(
  model=model,
  args=training_args,
  train_dataset=small_train_dataset,
  eval_dataset=small_eval_dataset,
    compute_metrics=compute_metrics
)
trainer.train()