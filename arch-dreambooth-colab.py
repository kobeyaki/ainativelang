#!/usr/bin/env python3
"""
Arch LoRA Fine-tune via Dreambooth
Copy this into Google Colab and run cell by cell
"""

# CELL 1: Install dependencies
import subprocess
subprocess.run(["pip", "install", "diffusers", "peft", "accelerate", "transformers", "torch", "torchvision", "tensorboard", "omegaconf"], check=True)

# CELL 2: Mount Google Drive (if using Colab)
try:
    from google.colab import drive
    drive.mount('/content/drive')
    DRIVE_MOUNTED = True
except:
    DRIVE_MOUNTED = False
    print("Not running in Colab, using local paths")

# CELL 3: Download training script
subprocess.run(["git", "clone", "https://github.com/huggingface/diffusers.git"], check=True)
import os
os.chdir("diffusers/examples/dreambooth")

# CELL 4: Prepare training data
# Upload 7 arch-neon images to Google Drive or local directory
# Path should be: /content/drive/MyDrive/arch_training/ (for Colab)
# Or: ./arch_training/ (for local)

TRAINING_DIR = "/content/drive/MyDrive/arch_training" if DRIVE_MOUNTED else "./arch_training"
os.makedirs(TRAINING_DIR, exist_ok=True)

print(f"Upload your 7 Arch images to: {TRAINING_DIR}")
print("Then run the next cell...")

# CELL 5: Run Dreambooth training
import subprocess

INSTANCE_PROMPT = "a photo of arch, neon orange star with cyan glow"
CLASS_PROMPT = "a photo of star character"
OUTPUT_DIR = "/content/drive/MyDrive/arch_lora" if DRIVE_MOUNTED else "./arch_lora"

cmd = [
    "python", "train_dreambooth_lora.py",
    "--pretrained_model_name_or_path", "stabilityai/stable-diffusion-xl-base-1.0",
    "--instance_data_dir", TRAINING_DIR,
    "--output_dir", OUTPUT_DIR,
    "--instance_prompt", INSTANCE_PROMPT,
    "--class_prompt", CLASS_PROMPT,
    "--class_data_dir", "/tmp/class_images",
    "--num_train_epochs", "100",
    "--train_batch_size", "1",
    "--gradient_accumulation_steps", "4",
    "--learning_rate", "1e-4",
    "--lr_scheduler", "constant",
    "--lr_warmup_steps", "0",
    "--mixed_precision", "bf16",
    "--use_8bit_adam",
    "--rank", "16",
]

subprocess.run(cmd, check=True)

print(f"\n✅ Training complete! Model saved to: {OUTPUT_DIR}")
print(f"Download the 'pytorch_lora_weights.safetensors' file from {OUTPUT_DIR}")
