import { useState } from 'react';
import { Send, Stethoscope, Thermometer, Hash, Zap } from 'lucide-react';
import type { ModelStatus } from '../hooks/useModel';

interface PromptPanelProps {
  status: ModelStatus;
  onGenerate: (prompt: string, maxTokens: number, temperature: number) => void;
}

const EXAMPLE_PROMPTS = [
  {
    label: 'Triage',
    icon: Stethoscope,
    prompt: 'Patient presents with severe chest pain radiating to left arm, shortness of breath, and diaphoresis. History of hypertension. Classify urgency level and explain reasoning:',
  },
  {
    label: 'Simplify',
    icon: Zap,
    prompt: 'Simplify this medical text for a patient: "The patient was diagnosed with acute myocardial infarction with ST-elevation in leads V1-V4, requiring emergent percutaneous coronary intervention."',
  },
  {
    label: 'Symptoms',
    icon: Thermometer,
    prompt: 'A 45-year-old female presents with persistent fatigue, unexplained weight gain, cold intolerance, and dry skin for the past 3 months. What are the most likely conditions and recommended initial tests?',
  },
];

export function PromptPanel({ status, onGenerate }: PromptPanelProps) {
  const [prompt, setPrompt] = useState('');
  const [maxTokens, setMaxTokens] = useState(256);
  const [temperature, setTemperature] = useState(0.7);

  const canGenerate = status === 'ready' && prompt.trim().length > 0;

  const handleSubmit = () => {
    if (canGenerate) {
      onGenerate(prompt, maxTokens, temperature);
    }
  };

  return (
    <div className="glass rounded-xl p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Prompt</h2>
        <div className="flex gap-2">
          {EXAMPLE_PROMPTS.map((ex) => (
            <button
              key={ex.label}
              onClick={() => setPrompt(ex.prompt)}
              className="flex items-center gap-1.5 px-2.5 py-1 text-xs rounded-lg bg-gray-800/50 text-gray-400 hover:text-cyan-400 hover:bg-gray-800 transition-colors border border-gray-700/50"
            >
              <ex.icon className="w-3 h-3" />
              {ex.label}
            </button>
          ))}
        </div>
      </div>

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleSubmit();
        }}
        placeholder="Enter a medical scenario..."
        rows={4}
        className="w-full bg-gray-900/50 rounded-lg px-4 py-3 text-sm text-gray-200 placeholder-gray-600 border border-gray-700/50 focus:border-cyan-500/50 focus:outline-none focus:ring-1 focus:ring-cyan-500/20 resize-none transition-colors"
      />

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <Hash className="w-3.5 h-3.5 text-gray-500" />
            <label className="text-xs text-gray-500">Tokens</label>
            <input
              type="range"
              min={32}
              max={512}
              step={32}
              value={maxTokens}
              onChange={(e) => setMaxTokens(Number(e.target.value))}
              className="w-20 accent-cyan-500"
            />
            <span className="text-xs font-mono text-gray-400 w-8">{maxTokens}</span>
          </div>
          <div className="flex items-center gap-2">
            <Thermometer className="w-3.5 h-3.5 text-gray-500" />
            <label className="text-xs text-gray-500">Temp</label>
            <input
              type="range"
              min={0}
              max={1.5}
              step={0.1}
              value={temperature}
              onChange={(e) => setTemperature(Number(e.target.value))}
              className="w-20 accent-violet-500"
            />
            <span className="text-xs font-mono text-gray-400 w-8">{temperature}</span>
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={!canGenerate}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-violet-600 text-white text-sm font-medium hover:from-cyan-500 hover:to-violet-500 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
        >
          <Send className="w-3.5 h-3.5" />
          Generate
          <span className="text-xs opacity-60 ml-1">Cmd+Enter</span>
        </button>
      </div>
    </div>
  );
}
