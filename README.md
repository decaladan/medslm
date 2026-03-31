# MedSLM - Browser-Based Blood Test Analysis

A small language model fine-tuned for Spanish-language blood test analysis, running entirely in the browser with zero API calls.

## Overview

MedSLM is a **Qwen3 0.6B** model fine-tuned via LoRA on Spanish medical blood marker analysis data. The model is converted to ONNX and runs client-side using [Transformers.js](https://huggingface.co/docs/transformers.js) + WebGPU. All inference happens on-device -- no data leaves the browser.

**Model:** [charlierun82/MedSLM-Qwen3-0.6B-Blood-ES](https://huggingface.co/charlierun82/MedSLM-Qwen3-0.6B-Blood-ES)

## Features

- On-device inference via WebGPU (fp16, ~1.4GB)
- Spanish-language blood marker analysis and recommendations
- Real-time token generation metrics
- PDF export of analysis results
- Zero backend, fully private

## Tech Stack

- **Frontend:** React 19, TypeScript, Tailwind CSS
- **3D:** Three.js, GSAP
- **ML:** Transformers.js, ONNX Runtime (WebGPU)
- **Build:** Vite
- **Deploy:** Vercel

## Getting Started

```bash
npm install
npm run dev
```

Requires a WebGPU-compatible browser (Chrome 113+, Edge 113+).

## Training Data

The `data/` directory contains the training datasets:

- `synthetic_blood_es.jsonl` - Synthetic Spanish blood test analysis samples
- `mimic_blood_es.jsonl` - Processed MIMIC-IV demo data
- `train_v2_merged.jsonl` - Merged training set
- `mlx_v2/` - MLX-formatted splits for fine-tuning

## Scripts

- `scripts/process_mimic.py` - Process raw MIMIC-IV CSV data
- `scripts/generate_dataset.py` - Generate synthetic training data
- `scripts/generate_dataset_v2.py` - V2 dataset generation with improved quality
- `scripts/merge_datasets.py` - Merge and deduplicate datasets
- `scripts/prepare_mlx_data.py` - Prepare train/test/valid splits for MLX
- `scripts/train.sh` - LoRA fine-tuning script

## License

All rights reserved.
