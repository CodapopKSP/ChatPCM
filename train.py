import gpt_2_simple as gpt2
import os
import requests

# Download or verify model
model_name = "124M"
checkpoint_dir = 'deep_based'
run_name = 'Key_Value0_1_plus3'

if not os.path.isdir(os.path.join("models", model_name)):
	print(f"Downloading {model_name} model...")
	gpt2.download_gpt2(model_name=model_name)

# Train model with dataset and save a checkpoint
file_name = "training_data/dataset_key_value/dataset3.json"
sess = gpt2.start_tf_sess()
gpt2.finetune(sess,
              file_name,
              model_name=model_name,
              steps=200,
              checkpoint_dir = 'Deep Based',
              run_name = 'Key_Value0')   # steps is max number of training steps

# Generate final example text
gpt2.generate(sess,
              checkpoint_dir = checkpoint_dir,
              run_name = run_name)