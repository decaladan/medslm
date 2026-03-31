import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Activity, Clock, Gauge, TrendingUp } from 'lucide-react';
import type { Metrics } from '../hooks/useModel';

interface MetricsPanelProps {
  metricsHistory: Metrics[];
}

export function MetricsPanel({ metricsHistory }: MetricsPanelProps) {
  if (metricsHistory.length === 0) {
    return (
      <div className="glass rounded-xl p-5">
        <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          Performance Metrics
        </h2>
        <p className="text-gray-600 text-sm mt-4 italic">Run a generation to see metrics...</p>
      </div>
    );
  }

  const latest = metricsHistory[metricsHistory.length - 1];
  const avgTokPerSec = metricsHistory.reduce((s, m) => s + m.tokensPerSec, 0) / metricsHistory.length;

  const chartData = metricsHistory.map((m, i) => ({
    name: `#${i + 1}`,
    tokensPerSec: parseFloat(m.tokensPerSec.toFixed(1)),
    latency: parseFloat(m.totalTime.toFixed(2)),
  }));

  return (
    <div className="glass rounded-xl p-5 space-y-4">
      <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider flex items-center gap-2">
        <Activity className="w-4 h-4 text-cyan-400" />
        Performance Metrics
      </h2>

      <div className="grid grid-cols-3 gap-3">
        <MetricCard
          icon={<Gauge className="w-4 h-4 text-cyan-400" />}
          label="Tokens/sec"
          value={latest.tokensPerSec.toFixed(1)}
          sub="latest"
        />
        <MetricCard
          icon={<Clock className="w-4 h-4 text-violet-400" />}
          label="Latency"
          value={`${latest.totalTime.toFixed(1)}s`}
          sub={`${latest.tokenCount} tokens`}
        />
        <MetricCard
          icon={<TrendingUp className="w-4 h-4 text-emerald-400" />}
          label="Avg tok/s"
          value={avgTokPerSec.toFixed(1)}
          sub={`${metricsHistory.length} runs`}
        />
      </div>

      {metricsHistory.length > 1 && (
        <div className="h-40">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <XAxis dataKey="name" tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} width={35} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid rgba(148,163,184,0.1)',
                  borderRadius: '8px',
                  fontSize: '12px',
                }}
                labelStyle={{ color: '#94a3b8' }}
              />
              <Bar dataKey="tokensPerSec" name="tok/s" radius={[4, 4, 0, 0]}>
                {chartData.map((_, i) => (
                  <Cell key={i} fill={i === chartData.length - 1 ? '#06b6d4' : '#1e3a5f'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

function MetricCard({ icon, label, value, sub }: { icon: React.ReactNode; label: string; value: string; sub: string }) {
  return (
    <div className="bg-gray-900/50 rounded-lg p-3 space-y-1">
      <div className="flex items-center gap-1.5">
        {icon}
        <span className="text-xs text-gray-500">{label}</span>
      </div>
      <p className="text-lg font-semibold font-mono text-gray-200">{value}</p>
      <p className="text-xs text-gray-600">{sub}</p>
    </div>
  );
}
