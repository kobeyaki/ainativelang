# Arch LoRA Fine-Tune via Google Colab

## Step 1: Create Colab Notebook
1. Go to https://colab.research.google.com
2. Click **"New notebook"**

## Step 2: Paste This Code

Copy everything below and paste into the first cell in Colab, then click **Run**:

```python
# CELL 1: Install everything
!pip install -q diffusers peft accelerate transformers torch torchvision tensorboard omegaconf xformers bitsandbytes

# CELL 2: Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# CELL 3: Clone Dreambooth
!git clone -q https://github.com/huggingface/diffusers.git
import os
os.chdir("/content/diffusers/examples/dreambooth")

# CELL 4: Upload images
print("✅ Go to Google Drive on your phone")
print("📁 Create folder: My Drive > arch_training")
print("📸 Upload your 7 arch-neon JPG images there")
print("⏳ Then come back and run the next cell when done")
```

## Step 3: Upload Images on Your Phone
1. Open Google Drive on your phone (app or browser)
2. Create folder: **arch_training** (in My Drive root)
3. Upload the 7 arch-neon images to that folder
4. Come back to Colab

## Step 4: Run Training

Paste this into next cell in Colab:

```python
# CELL 5: Train the model
!python train_dreambooth_lora.py \
  --pretrained_model_name_or_path="stabilityai/stable-diffusion-xl-base-1.0" \
  --instance_data_dir="/content/drive/MyDrive/arch_training" \
  --output_dir="/content/drive/MyDrive/arch_lora_output" \
  --instance_prompt="a photo of arch, neon orange star with cyan glow" \
  --class_prompt="a photo of star character" \
  --num_train_epochs="100" \
  --train_batch_size="1" \
  --gradient_accumulation_steps="4" \
  --learning_rate="1e-4" \
  --lr_scheduler="constant" \
  --mixed_precision="bf16" \
  --rank="16"

print("✅ Training complete!")
print("📁 Model saved to: /content/drive/MyDrive/arch_lora_output/")
print("📥 Go to Google Drive and download pytorch_lora_weights.safetensors")
```

## Step 5: Download Model
1. When training finishes, go to Google Drive
2. Open **arch_lora_output** folder
3. Download **pytorch_lora_weights.safetensors** (the trained model)
4. Send me the file or keep it safe

---

**Timeline:**
- Install: 2 min
- Upload images: 5 min
- Training: 30 min
- Download: 2 min
- **Total: ~40 min**

**That's it. You'll have a trained Arch LoRA model ready to generate infinite variations.**
