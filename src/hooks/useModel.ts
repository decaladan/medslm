import { useState, useRef, useCallback, useEffect } from 'react';

export interface Metrics {
  tokenCount: number;
  totalTime: number;
  tokensPerSec: number;
  timestamp: number;
}

export type ModelStatus = 'idle' | 'loading' | 'ready' | 'generating' | 'error';

interface LoadProgress {
  file: string;
  loaded: number;
  total: number;
  progress: number;
}

const SYSTEM_PROMPT =
  'IMPORTANTE: Responde SIEMPRE en español. ' +
  'Eres un asistente medico especializado en analisis de sangre. ' +
  'Analizas los resultados de analiticas y proporcionas recomendaciones ' +
  'personalizadas de dieta y estilo de vida basadas en los valores. ' +
  'Para cada valor alterado, explica que significa y da recomendaciones concretas de alimentacion. ' +
  'Usa formato con marcadores (**negrita** para los nombres de marcadores). ' +
  'Siempre recuerdas al paciente que estas recomendaciones son orientativas ' +
  'y no sustituyen el consejo de su medico. ' +
  'Responde unicamente en español.';

export function useModel() {
  const workerRef = useRef<Worker | null>(null);
  const [status, setStatus] = useState<ModelStatus>('idle');
  const [statusMessage, setStatusMessage] = useState('');
  const [loadProgress, setLoadProgress] = useState<LoadProgress | null>(null);
  const [currentOutput, setCurrentOutput] = useState('');
  const [liveMetrics, setLiveMetrics] = useState<{ tokenCount: number; elapsed: number; tokensPerSec: number } | null>(null);
  const [metricsHistory, setMetricsHistory] = useState<Metrics[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const worker = new Worker(new URL('../workers/model.worker.ts', import.meta.url), {
      type: 'module',
    });

    worker.onmessage = (e) => {
      const msg = e.data;

      switch (msg.type) {
        case 'status':
          setStatus(msg.status);
          setStatusMessage(msg.message);
          if (msg.status === 'ready') {
            setLoadProgress(null);
          }
          break;
        case 'progress':
          setLoadProgress(msg);
          break;
        case 'token_update':
          setLiveMetrics({
            tokenCount: msg.tokenCount,
            elapsed: msg.elapsed,
            tokensPerSec: msg.tokensPerSec,
          });
          break;
        case 'result':
          setCurrentOutput(msg.text);
          setMetricsHistory((prev) => [...prev, msg.metrics]);
          setLiveMetrics(null);
          break;
        case 'error':
          setStatus('error');
          setError(msg.error);
          break;
      }
    };

    workerRef.current = worker;
    return () => worker.terminate();
  }, []);

  const loadModel = useCallback((modelId: string, dtype?: string) => {
    setError(null);
    setStatus('loading');
    workerRef.current?.postMessage({ type: 'load', model: modelId, dtype });
  }, []);

  const generate = useCallback((prompt: string, maxTokens = 256, temperature = 0.7) => {
    setCurrentOutput('');
    setError(null);
    workerRef.current?.postMessage({
      type: 'generate',
      prompt,
      maxTokens,
      temperature,
      systemPrompt: SYSTEM_PROMPT,
    });
  }, []);

  return {
    status,
    statusMessage,
    loadProgress,
    currentOutput,
    liveMetrics,
    metricsHistory,
    error,
    loadModel,
    generate,
  };
}
