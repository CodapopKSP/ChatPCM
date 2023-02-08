import os
import gpt_2_simple as gpt2

# Download or verify model
model_name = "124M"
checkpoint_dir = 'deep_based'
run_name = 'based100k_pruned_v2-high_LR2'

if not os.path.isdir(os.path.join("models", model_name)):
	print(f"Downloading {model_name} model...")
	gpt2.download_gpt2(model_name=model_name)

# Train model with dataset and save a checkpoint
file_name = "training_data/dataset_based_100k_pruned_v2/dataset8.json"
sess = gpt2.start_tf_sess()
gpt2.finetune(sess,
              file_name,
              model_name=model_name,
              steps=1000,
              checkpoint_dir = checkpoint_dir,
              #only_train_transformer_layers = True,
              learning_rate=0.0001,
              run_name = run_name)   # steps is max number of training steps

# Generate final example text
gpt2.generate(sess,
              checkpoint_dir = checkpoint_dir,
              run_name = run_name)

# Dataset Blacklist
# Based (under 100 chars)
# Based and pilled (under 100 chars)
# Good Bot
# Uncommon unicode characters
# Bot comments