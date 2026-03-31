"""
Prepare training data for mlx-lm LoRA fine-tuning.
Converts our blood test JSONL into chat format expected by mlx-lm.
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

SYSTEM_PROMPT = (
    "Eres un asistente médico especializado en análisis de sangre. "
    "Analizas los resultados de analíticas y proporcionas recomendaciones "
    "personalizadas de dieta y estilo de vida basadas en los valores. "
    "Siempre recuerdas al paciente que estas recomendaciones son orientativas "
    "y no sustituyen el consejo de su médico."
)

def convert_to_chat(input_path: str, output_path: str):
    samples = []
    with open(input_path, 'r') as f:
        for line in f:
            item = json.loads(line)
            chat = {
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": item["input"]},
                    {"role": "assistant", "content": item["output"]},
                ]
            }
            samples.append(chat)

    with open(output_path, 'w') as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + '\n')

    print(f"  {input_path} -> {output_path} ({len(samples)} samples)")

def main():
    os.makedirs(os.path.join(DATA_DIR, 'mlx'), exist_ok=True)

    print("Converting datasets to mlx-lm chat format...")
    convert_to_chat(
        os.path.join(DATA_DIR, 'train.jsonl'),
        os.path.join(DATA_DIR, 'mlx', 'train.jsonl'),
    )
    convert_to_chat(
        os.path.join(DATA_DIR, 'test.jsonl'),
        os.path.join(DATA_DIR, 'mlx', 'valid.jsonl'),
    )
    # mlx-lm also expects a test split
    convert_to_chat(
        os.path.join(DATA_DIR, 'test.jsonl'),
        os.path.join(DATA_DIR, 'mlx', 'test.jsonl'),
    )
    print("Done!")

if __name__ == '__main__':
    main()
