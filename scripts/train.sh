#!/bin/bash
# Fine-tune SmolLM2-360M-Instruct on blood test data using LoRA on Apple Silicon
set -e

cd "$(dirname "$0")/.."

echo "Starting LoRA fine-tuning on Apple Silicon (MLX)..."
echo "Model: HuggingFaceTB/SmolLM2-360M-Instruct"
echo "Dataset: data/mlx/ ($(wc -l < data/mlx/train.jsonl) training samples)"
echo ""

mlx_lm.lora \
  --model HuggingFaceTB/SmolLM2-360M-Instruct \
  --data data/mlx \
  --train \
  --iters 600 \
  --batch-size 1 \
  --num-layers 8 \
  --learning-rate 2e-4 \
  --val-batches 10 \
  --steps-per-eval 100 \
  --max-seq-length 512 \
  --grad-checkpoint \
  --adapter-path models/blood-lora \
  --seed 42

echo ""
echo "Training complete! Adapter saved to models/blood-lora/"
echo ""
echo "Fusing adapter into model..."

mlx_lm.fuse \
  --model HuggingFaceTB/SmolLM2-360M-Instruct \
  --adapter-path models/blood-lora \
  --save-path models/MedSLM-360M-Blood-ES

echo "Fused model saved to models/MedSLM-360M-Blood-ES/"
echo "Done!"
