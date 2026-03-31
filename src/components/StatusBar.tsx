import { Shield, Cpu, Wifi, WifiOff } from 'lucide-react';
import type { ModelStatus } from '../hooks/useModel';

interface StatusBarProps {
  status: ModelStatus;
  message: string;
}

const statusConfig: Record<ModelStatus, { color: string; bg: string; label: string }> = {
  idle: { color: 'text-gray-400', bg: 'bg-gray-400', label: 'Idle' },
  loading: { color: 'text-amber-400', bg: 'bg-amber-400', label: 'Loading' },
  ready: { color: 'text-emerald-400', bg: 'bg-emerald-400', label: 'Ready' },
  generating: { color: 'text-cyan-400', bg: 'bg-cyan-400', label: 'Generating' },
  error: { color: 'text-red-400', bg: 'bg-red-400', label: 'Error' },
};

export function StatusBar({ status, message }: StatusBarProps) {
  const config = statusConfig[status];

  return (
    <div className="glass rounded-xl px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${config.bg} ${status === 'generating' ? 'animate-glow-pulse' : ''}`} />
          <span className={`text-sm font-medium ${config.color}`}>{config.label}</span>
        </div>
        <span className="text-xs text-gray-500">|</span>
        <span className="text-xs text-gray-400">{message}</span>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5 text-xs text-gray-400">
          <Shield className="w-3.5 h-3.5 text-emerald-400" />
          <span>Private</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-gray-400">
          <Cpu className="w-3.5 h-3.5 text-violet-400" />
          <span>WebGPU</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-gray-400">
          {status === 'idle' ? (
            <WifiOff className="w-3.5 h-3.5 text-gray-500" />
          ) : (
            <Wifi className="w-3.5 h-3.5 text-cyan-400" />
          )}
          <span>Browser-only</span>
        </div>
      </div>
    </div>
  );
}
