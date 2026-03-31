import { pipeline, TextGenerationPipeline, env } from '@huggingface/transformers';

env.allowLocalModels = false;

let generator: TextGenerationPipeline | null = null;
let currentModelId: string | null = null;

// Known total model size in bytes (~1.4GB fp16)
const MODEL_TOTAL_BYTES = 1_500_000_000;

// Track cumulative download progress across all files
const fileProgress: Record<string, number> = {};

interface LoadMessage {
  type: 'load';
  model: string;
  dtype?: string;
}

interface GenerateMessage {
  type: 'generate';
  prompt: string;
  maxTokens: number;
  temperature: number;
  systemPrompt?: string;
}

type WorkerMessage = LoadMessage | GenerateMessage;

async function loadModel(modelId: string, dtype: string = 'q4f16') {
  if (currentModelId === modelId && generator) {
    self.postMessage({ type: 'status', status: 'ready', message: 'Model ready' });
    return;
  }

  if (generator) {
    try { await generator.dispose(); } catch { /* ignore */ }
    generator = null;
  }

  // Reset progress tracking
  Object.keys(fileProgress).forEach((k) => delete fileProgress[k]);

  self.postMessage({ type: 'status', status: 'loading', message: 'Downloading model...' });

  generator = await (pipeline as Function)('text-generation', modelId, {
    dtype: dtype,
    device: 'webgpu',
    progress_callback: (progress: Record<string, unknown>) => {
      if (progress.status === 'progress') {
        const file = String(progress.file || '');
        const loaded = Number(progress.loaded || 0);

        // Track per-file loaded bytes
        fileProgress[file] = loaded;

        // Sum all file progress for overall %
        const totalLoaded = Object.values(fileProgress).reduce((a, b) => a + b, 0);
        const overallPercent = Math.min((totalLoaded / MODEL_TOTAL_BYTES) * 100, 99.9);

        self.postMessage({
          type: 'progress',
          file,
          loaded: totalLoaded,
          total: MODEL_TOTAL_BYTES,
          progress: overallPercent,
        });
      } else if (progress.status === 'done') {
        self.postMessage({ type: 'status', status: 'loading', message: `Loaded ${progress.file}` });
      }
    },
  }) as TextGenerationPipeline;

  currentModelId = modelId;
  self.postMessage({ type: 'status', status: 'ready', message: 'Model ready' });
}

/**
 * Manually build Qwen3 chat format as fallback when tokenizer.chat_template is missing.
 */
function buildChatText(messages: Array<{ role: string; content: string }>): string {
  let text = '';
  for (const msg of messages) {
    text += `<|im_start|>${msg.role}\n${msg.content}<|im_end|>\n`;
  }
  text += '<|im_start|>assistant\n';
  return text;
}

async function generate(prompt: string, maxTokens: number, temperature: number, systemPrompt?: string) {
  if (!generator) {
    self.postMessage({ type: 'error', error: 'Model not loaded' });
    return;
  }

  self.postMessage({ type: 'status', status: 'generating', message: 'Generating...' });

  const startTime = performance.now();
  let tokenCount = 0;

  // Build chat messages for the model
  const messages: Array<{ role: string; content: string }> = [];
  if (systemPrompt) {
    messages.push({ role: 'system', content: systemPrompt });
  }
  messages.push({ role: 'user', content: prompt });

  // Apply chat template — try tokenizer first, fall back to manual Qwen3 format
  const tokenizer = generator.tokenizer;
  let chatText: string;
  try {
    console.log('[worker] Applying chat template...');
    chatText = (tokenizer.apply_chat_template as Function)(messages, {
      tokenize: false,
      add_generation_prompt: true,
      enable_thinking: false,
    }) as string;
    console.log('[worker] Chat text length:', chatText.length);
  } catch (e) {
    const errMsg = e instanceof Error ? e.message : String(e);
    console.warn('[worker] Chat template failed, using manual Qwen3 format:', errMsg);
    chatText = buildChatText(messages);
    console.log('[worker] Manual chat text length:', chatText.length);
  }

  console.log('[worker] Starting generation...');
  let output;
  try {
    output = await (generator as Function)(chatText, {
      max_new_tokens: maxTokens,
      temperature: temperature,
      do_sample: temperature > 0,
      return_full_text: false,
      callback_function: (beams: unknown) => {
        // Handle different callback shapes from Transformers.js
        if (Array.isArray(beams) && beams[0]?.output_token_ids) {
          tokenCount = beams[0].output_token_ids.length;
        } else {
          // Fallback: just increment
          tokenCount++;
        }
        const elapsed = (performance.now() - startTime) / 1000;
        const tokensPerSec = tokenCount / elapsed;

        self.postMessage({
          type: 'token_update',
          tokenCount,
          elapsed,
          tokensPerSec,
        });
      },
    });
    console.log('[worker] Generation complete, tokens:', tokenCount);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    console.error('[worker] Generation error:', msg);
    self.postMessage({ type: 'error', error: msg });
    self.postMessage({ type: 'status', status: 'ready', message: 'Ready' });
    return;
  }

  const totalTime = (performance.now() - startTime) / 1000;

  // If callback never fired, estimate tokens from output
  if (tokenCount === 0 && Array.isArray(output) && output.length > 0) {
    const result = output[0] as { generated_text: string };
    const genText = typeof result.generated_text === 'string' ? result.generated_text : '';
    // Rough estimate: ~4 chars per token
    tokenCount = Math.max(1, Math.round(genText.length / 4));
    console.log('[worker] Token count estimated from output length:', tokenCount);
  }

  const finalTokensPerSec = tokenCount > 0 ? tokenCount / totalTime : 0;

  let text = '';
  if (Array.isArray(output) && output.length > 0) {
    const result = output[0] as { generated_text: string };
    text = typeof result.generated_text === 'string' ? result.generated_text : '';
  }

  // Strip Qwen3 <think> tags and any leftover special tokens
  text = text.replace(/<think>[\s\S]*?<\/think>\s*/g, '').trim();
  text = text.replace(/<\|im_end\|>/g, '').trim();
  text = text.replace(/<\|endoftext\|>/g, '').trim();

  self.postMessage({
    type: 'result',
    text,
    metrics: {
      tokenCount,
      totalTime,
      tokensPerSec: finalTokensPerSec,
      timestamp: Date.now(),
    },
  });

  self.postMessage({ type: 'status', status: 'ready', message: 'Ready' });
}

self.onmessage = async (e: MessageEvent<WorkerMessage>) => {
  const { type } = e.data;

  try {
    if (type === 'load') {
      await loadModel(e.data.model, e.data.dtype);
    } else if (type === 'generate') {
      await generate(e.data.prompt, e.data.maxTokens, e.data.temperature, e.data.systemPrompt);
    }
  } catch (error) {
    self.postMessage({
      type: 'error',
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
};
