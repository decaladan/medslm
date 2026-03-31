#!/usr/bin/env python3
"""
Merge synthetic and MIMIC blood test datasets into a single training set.
Keeps the synthetic test set separate for evaluation.
"""

import json
import os
import random
import shutil

SEED = 42
random.seed(SEED)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SYNTHETIC_TRAIN = os.path.join(DATA_DIR, "synthetic_blood_es.jsonl")
MIMIC_TRAIN = os.path.join(DATA_DIR, "mimic_blood_es.jsonl")
SYNTHETIC_TEST = os.path.join(DATA_DIR, "synthetic_blood_es_test.jsonl")

OUTPUT_TRAIN = os.path.join(DATA_DIR, "train.jsonl")
OUTPUT_TEST = os.path.join(DATA_DIR, "test.jsonl")


def read_jsonl(path):
    samples = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                samples.append(json.loads(line))
    return samples


def write_jsonl(path, samples):
    with open(path, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")


def main():
    print("Loading datasets...")

    synthetic_train = read_jsonl(SYNTHETIC_TRAIN)
    print(f"  Synthetic training samples: {len(synthetic_train)}")

    mimic_train = read_jsonl(MIMIC_TRAIN)
    print(f"  MIMIC training samples: {len(mimic_train)}")

    synthetic_test = read_jsonl(SYNTHETIC_TEST)
    print(f"  Synthetic test samples: {len(synthetic_test)}")

    # Merge and shuffle training sets
    merged_train = synthetic_train + mimic_train
    random.shuffle(merged_train)

    print(f"\nMerged training set: {len(merged_train)} samples")

    # Write merged training set
    write_jsonl(OUTPUT_TRAIN, merged_train)
    print(f"  Saved to: {OUTPUT_TRAIN}")

    # Copy test set
    shutil.copy2(SYNTHETIC_TEST, OUTPUT_TEST)
    print(f"  Test set copied to: {OUTPUT_TEST}")
    print(f"  Test set size: {len(synthetic_test)} samples")

    # Summary stats
    print(f"\n{'='*50}")
    print(f"FINAL DATASET SUMMARY")
    print(f"{'='*50}")
    print(f"  Training set (train.jsonl): {len(merged_train)} samples")
    print(f"    - From synthetic: {len(synthetic_train)}")
    print(f"    - From MIMIC-IV:  {len(mimic_train)}")
    print(f"  Test set (test.jsonl):      {len(synthetic_test)} samples")
    print(f"  Total:                      {len(merged_train) + len(synthetic_test)} samples")

    # Check marker distribution in merged training
    marker_freq = {}
    for s in merged_train:
        for m in s["markers"]:
            marker_freq[m] = marker_freq.get(m, 0) + 1

    print(f"\nMarker frequency in training set:")
    for name, count in sorted(marker_freq.items(), key=lambda x: -x[1]):
        print(f"    {name}: {count}")


if __name__ == "__main__":
    main()
