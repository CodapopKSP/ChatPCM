import gpt_2_simple as gpt2
import os
import requests

# Download or verify model
model_name = "124M"
if not os.path.isdir(os.path.join("models", model_name)):
	print(f"Downloading {model_name} model...")
	gpt2.download_gpt2(model_name=model_name)

# Train model with dataset and save a checkpoint
file_name = "dataset.txt"
sess = gpt2.start_tf_sess()
gpt2.finetune(sess,
              file_name,
              model_name=model_name,
              steps=1000)   # steps is max number of training steps

# Generate final example text
gpt2.generate(sess)