import { useState, useEffect } from 'react';
import { jsPDF } from 'jspdf';
import type { ModelStatus, Metrics } from '../hooks/useModel';

interface OutputPanelProps {
  output: string;
  status: ModelStatus;
  liveMetrics: { tokenCount: number; elapsed: number; tokensPerSec: number } | null;
  metricsHistory: Metrics[];
  onBack: () => void;
  analyzedPrompt: string;
}

const ANALYZING_LINES = [
  'Analyzing sample data...',
  'Identifying key biomarkers...',
  'Calculating morphological indices...',
  'Comparing against reference ranges...',
  'Running AI model inferences...',
  'Generating detailed report...',
  'Detecting potential anomalies...',
  'Correlating findings with clinical data...',
  'AI Model: MedSLM activated...',
  'Deep learning neural inference...',
  'Processing...',
  'Patient data encrypted...',
  'Secure encrypted transmission enabled...',
];

export function OutputPanel({ output, status, liveMetrics, metricsHistory, onBack, analyzedPrompt }: OutputPanelProps) {
  const isGenerating = status === 'generating';
  const hasOutput = output && output.trim().length > 0;
  const latestMetrics = metricsHistory.length > 0 ? metricsHistory[metricsHistory.length - 1] : null;
  const markers = parseMarkers(analyzedPrompt);

  if (isGenerating && !hasOutput) {
    return <AnalyzingView liveMetrics={liveMetrics} />;
  }

  if (hasOutput) {
    return <ResultsView output={output} metrics={latestMetrics} onBack={onBack} markers={markers} />;
  }

  return null;
}

// --- Analyzing Screen ---

function AnalyzingView({ liveMetrics }: { liveMetrics: OutputPanelProps['liveMetrics'] }) {
  const [visibleLines, setVisibleLines] = useState<number>(0);

  useEffect(() => {
    setVisibleLines(0);
    const interval = setInterval(() => {
      setVisibleLines((prev) => prev >= ANALYZING_LINES.length ? prev : prev + 1);
    }, 800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-[60vh] flex items-center justify-center px-2">
      <div className="border-2 border-black bg-white w-full max-w-4xl">
        <div className="grid grid-cols-1 md:grid-cols-2">
          <div className="p-6 md:p-10 flex flex-col justify-center border-b-2 md:border-b-0 md:border-r-2 border-black">
            <div className="flex items-center gap-3 mb-6 md:mb-8">
              <div className="w-4 h-4 md:w-5 md:h-5 bg-[#ff6600] rounded-full animate-pulse-dot" />
              <span className="text-3xl md:text-5xl font-bold uppercase tracking-tight">ANALYZING</span>
            </div>
            {liveMetrics && (
              <div className="space-y-2 font-mono text-xs text-gray-500">
                <div>Tokens: {liveMetrics.tokenCount}</div>
                <div>Speed: {liveMetrics.tokensPerSec.toFixed(1)} tok/s</div>
                <div>Elapsed: {liveMetrics.elapsed.toFixed(1)}s</div>
              </div>
            )}
            <p className="font-mono text-[10px] text-gray-400 mt-6 md:mt-8 uppercase tracking-widest">
              Model running on your GPU via WebGPU
            </p>
          </div>
          <div className="p-6 md:p-8 bg-gray-50 font-mono text-xs text-gray-600 space-y-1.5 min-h-[250px] md:min-h-[350px]">
            {ANALYZING_LINES.slice(0, visibleLines).map((line, i) => (
              <div key={i} className="animate-fade-in">
                <span className="text-gray-400">{'>'}</span> {line}
              </div>
            ))}
            {visibleLines < ANALYZING_LINES.length && (
              <span className="animate-cursor text-[#ff6600]">_</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// --- Results Screen ---

interface AnalyzedMarker {
  name: string;
  value: number;
  unit: string;
  status: 'low' | 'normal' | 'high';
}

const DOT_COLORS = {
  low: 'bg-blue-500',
  normal: 'bg-emerald-500',
  high: 'bg-[#ff6600]',
};

// --- PDF Generation ---

function generatePDF(markers: AnalyzedMarker[], sections: { title: string; items: string[] }[]) {
  const doc = new jsPDF({ unit: 'mm', format: 'a4' });
  const pageW = doc.internal.pageSize.getWidth();
  const pageH = doc.internal.pageSize.getHeight();
  const margin = 20;
  const contentW = pageW - margin * 2;
  let y = margin;

  // --- Header bar ---
  doc.setFillColor(0, 0, 0);
  doc.rect(0, 0, pageW, 28, 'F');
  doc.setFontSize(20);
  doc.setTextColor(255, 102, 0);
  doc.text('MEDSLM', margin, 18);
  doc.setFontSize(9);
  doc.setTextColor(180, 180, 180);
  doc.text('BLOOD TEST ANALYSIS REPORT', pageW - margin, 13, { align: 'right' });
  doc.text(new Date().toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' }).toUpperCase(), pageW - margin, 19, { align: 'right' });
  y = 38;

  // --- Orange accent line ---
  doc.setFillColor(255, 102, 0);
  doc.rect(margin, y, contentW, 1.5, 'F');
  y += 8;

  // --- Marker cards ---
  if (markers.length > 0) {
    doc.setFontSize(8);
    doc.setTextColor(150, 150, 150);
    doc.text('BIOMARKER VALUES', margin, y);
    y += 6;

    const cols = 3;
    const cardW = (contentW - (cols - 1) * 4) / cols;
    const cardH = 22;

    markers.forEach((m, i) => {
      const col = i % cols;
      const row = Math.floor(i / cols);
      const cx = margin + col * (cardW + 4);
      const cy = y + row * (cardH + 4);

      // Check page overflow
      if (cy + cardH > pageH - margin) {
        doc.addPage();
        y = margin;
      }

      // Card background
      doc.setFillColor(248, 248, 248);
      doc.roundedRect(cx, cy, cardW, cardH, 2, 2, 'F');

      // Card border
      doc.setDrawColor(220, 220, 220);
      doc.setLineWidth(0.3);
      doc.roundedRect(cx, cy, cardW, cardH, 2, 2, 'S');

      // Status dot
      if (m.status === 'high') doc.setFillColor(255, 102, 0);
      else if (m.status === 'low') doc.setFillColor(59, 130, 246);
      else doc.setFillColor(16, 185, 129);
      doc.circle(cx + cardW - 5, cy + 5, 1.5, 'F');

      // Value
      doc.setFontSize(16);
      doc.setTextColor(30, 30, 30);
      doc.text(String(m.value), cx + 4, cy + 13);

      // Unit
      doc.setFontSize(7);
      doc.setTextColor(150, 150, 150);
      doc.text(m.unit, cx + 4 + doc.getTextWidth(String(m.value)) * (16 / 7) + 2, cy + 13);

      // Name
      doc.setFontSize(7);
      doc.setTextColor(100, 100, 100);
      doc.text(m.name.toUpperCase(), cx + 4, cy + 19);
    });

    const totalRows = Math.ceil(markers.length / cols);
    y += totalRows * (cardH + 4) + 6;
  }

  // Check page space
  if (y > pageH - 60) {
    doc.addPage();
    y = margin;
  }

  // --- Separator ---
  doc.setFillColor(255, 102, 0);
  doc.rect(margin, y, contentW, 0.5, 'F');
  y += 8;

  // --- Recommendations ---
  if (sections.length > 0) {
    doc.setFontSize(8);
    doc.setTextColor(150, 150, 150);
    doc.text('AI RECOMMENDATIONS', margin, y);
    y += 7;

    for (const section of sections) {
      if (y > pageH - 30) {
        doc.addPage();
        y = margin;
      }

      doc.setFontSize(11);
      doc.setTextColor(30, 30, 30);
      doc.text(section.title.toUpperCase(), margin, y);
      y += 6;

      for (const item of section.items) {
        if (y > pageH - 20) {
          doc.addPage();
          y = margin;
        }

        // Orange bullet
        doc.setFillColor(255, 102, 0);
        doc.rect(margin, y - 2, 2, 2, 'F');

        // Wrap text
        doc.setFontSize(9);
        doc.setTextColor(70, 70, 70);
        const lines = doc.splitTextToSize(item, contentW - 8);
        doc.text(lines, margin + 6, y);
        y += lines.length * 4.5 + 2;
      }
      y += 4;
    }
  }

  // --- Footer on last page ---
  doc.setFillColor(245, 245, 245);
  doc.rect(0, pageH - 18, pageW, 18, 'F');
  doc.setFontSize(6.5);
  doc.setTextColor(160, 160, 160);
  doc.text(
    'AVISO: Estas recomendaciones son orientativas y no sustituyen el consejo de un profesional medico.',
    margin, pageH - 11
  );
  doc.text(
    'ON-DEVICE AI • PRIVATE • ZERO DATA SENT • MEDSLM v0.1',
    margin, pageH - 7
  );

  doc.save('medslm-report.pdf');
}

function ResultsView({ output, metrics, onBack, markers }: {
  output: string;
  metrics: Metrics | null;
  onBack: () => void;
  markers: AnalyzedMarker[];
}) {
  const sections = parseOutput(output);

  const handleExport = () => {
    generatePDF(markers, sections);
  };

  return (
    <div className="space-y-0">
      {/* Header */}
      <div className="border-2 border-black bg-white px-4 py-3 md:px-6 md:py-5 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 md:gap-3 min-w-0">
          <div className="w-8 h-8 md:w-10 md:h-10 bg-emerald-500 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-white text-sm md:text-lg font-bold">&#10003;</span>
          </div>
          <h2 className="text-xl md:text-4xl font-bold uppercase tracking-tighter truncate">ANALYSIS COMPLETE</h2>
        </div>
        {metrics && (
          <div className="text-right font-mono text-[10px] text-gray-400 uppercase space-y-0.5 flex-shrink-0 hidden sm:block">
            <div>{metrics.tokenCount} tokens</div>
            <div>{metrics.tokensPerSec.toFixed(1)} tok/s</div>
            <div>{metrics.totalTime.toFixed(1)}s</div>
          </div>
        )}
      </div>

      {/* Two-column body */}
      <div className="border-2 border-t-0 border-black bg-white">
        <div className="grid grid-cols-1 lg:grid-cols-2">
          {/* Left: Marker value cards */}
          <div className="p-3 md:p-5 border-b-2 lg:border-b-0 lg:border-r-2 border-black">
            <div className="grid grid-cols-2 gap-2 md:gap-3">
              {markers.map((m) => (
                <div key={m.name} className="border-2 border-gray-300 rounded-lg p-2 md:p-3 relative">
                  <div className="absolute top-2 right-2">
                    <div className={`w-2.5 h-2.5 md:w-3 md:h-3 rounded-sm ${DOT_COLORS[m.status]}`} />
                  </div>
                  <div className="flex items-baseline gap-1">
                    <span className="text-xl md:text-3xl font-bold font-mono">{m.value}</span>
                    <span className="text-[9px] md:text-xs font-mono text-gray-400">{m.unit}</span>
                  </div>
                  <div className="text-[9px] md:text-[11px] font-bold text-gray-600 mt-0.5 md:mt-1">{m.name}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Right: Recommendations */}
          <div className="p-3 md:p-5">
            {sections.length > 0 ? (
              <div className="space-y-5 md:space-y-6">
                {sections.map((section, i) => (
                  <div key={i}>
                    <h3 className="text-base md:text-lg font-bold uppercase tracking-wide mb-2 md:mb-3">{section.title}</h3>
                    <ul className="space-y-1.5 md:space-y-2">
                      {section.items.map((item, j) => (
                        <li key={j} className="flex items-start gap-2 md:gap-2.5 text-xs md:text-sm">
                          <span className="w-2 h-2 md:w-2.5 md:h-2.5 bg-[#ff6600] rounded-sm mt-0.5 md:mt-1 flex-shrink-0" />
                          <span className="text-gray-700 leading-relaxed">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            ) : (
              <div className="font-mono text-xs md:text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                {output}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="border-2 border-t-0 border-black bg-gray-50 px-4 md:px-6 py-3">
        <p className="font-mono text-[9px] md:text-[10px] text-gray-400 leading-relaxed">
          AVISO: Estas recomendaciones son orientativas y no sustituyen el consejo de un profesional medico.
          Consulte siempre con su medico antes de realizar cambios en su dieta o estilo de vida.
        </p>
      </div>

      {/* Actions */}
      <div className="border-2 border-t-0 border-black bg-white flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 px-4 md:px-6 py-3 md:py-4">
        <button onClick={onBack}
          className="px-4 md:px-5 py-2 border-2 border-black text-xs font-bold uppercase tracking-wider hover:bg-black hover:text-white transition-colors">
          ← NEW ANALYSIS
        </button>
        <div className="flex items-center gap-3">
          <span className="font-mono text-[10px] text-gray-400 uppercase tracking-widest hidden md:inline">
            ON-DEVICE • PRIVATE • ZERO DATA SENT
          </span>
          <button
            onClick={handleExport}
            className="px-4 md:px-5 py-2 bg-[#ff6600] text-white text-xs font-bold uppercase tracking-wider hover:bg-[#e55b00] transition-colors w-full sm:w-auto">
            EXPORT PDF
          </button>
        </div>
      </div>
    </div>
  );
}

// --- Parsers ---

/**
 * Extract marker values from the prompt we sent to the model.
 * Format: "- Glucosa: 142 mg/dL [ALTO] (ref: 70-100)"
 */
function parseMarkers(prompt: string): AnalyzedMarker[] {
  const markers: AnalyzedMarker[] = [];
  const lines = prompt.split('\n');
  for (const line of lines) {
    const match = line.match(/^- (.+?):\s*([\d.]+)\s*(.+?)\s*\[(.+?)\]/);
    if (match) {
      const statusLabel = match[4].trim().toUpperCase();
      let st: 'low' | 'normal' | 'high' = 'normal';
      if (statusLabel === 'ALTO') st = 'high';
      else if (statusLabel === 'BAJO') st = 'low';
      markers.push({
        name: match[1].trim(),
        value: parseFloat(match[2]),
        unit: match[3].trim(),
        status: st,
      });
    }
  }
  return markers;
}

function parseOutput(text: string): { title: string; items: string[] }[] {
  const sections: { title: string; items: string[] }[] = [];
  const lines = text.split('\n');
  let currentSection: { title: string; items: string[] } | null = null;

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;

    // Section headers: **Header**, ## Header, or CAPS HEADER:
    const boldMatch = trimmed.match(/^\*\*(.+?)\*\*:?\s*(-\s*.+)?$/);
    const hashMatch = trimmed.match(/^#{1,3}\s+(.+)$/);
    const capsMatch = trimmed.match(/^([A-ZÁÉÍÓÚÑ\s]{4,}):?\s*$/);

    if (boldMatch || hashMatch || capsMatch) {
      const title = (boldMatch?.[1] || hashMatch?.[1] || capsMatch?.[1] || '').trim();
      if (currentSection && currentSection.items.length > 0) {
        sections.push(currentSection);
      }
      currentSection = { title, items: [] };
      if (boldMatch?.[2]) {
        currentSection.items.push(boldMatch[2].replace(/^-\s*/, '').replace(/\*\*/g, ''));
      }
      continue;
    }

    // Also detect: **Something** (value) - STATUS:
    const markerHeader = trimmed.match(/^\*\*(.+?)\*\*\s*\(.+?\)\s*[-–]\s*\w+:?\s*$/);
    if (markerHeader) {
      if (currentSection && currentSection.items.length > 0) {
        sections.push(currentSection);
      }
      currentSection = { title: markerHeader[1].trim(), items: [] };
      continue;
    }

    const itemMatch = trimmed.match(/^[-*•]\s+(.+)/) || trimmed.match(/^\d+[.)]\s+(.+)/);
    if (itemMatch && currentSection) {
      currentSection.items.push(itemMatch[1].replace(/\*\*/g, ''));
      continue;
    }

    if (currentSection) {
      currentSection.items.push(trimmed.replace(/\*\*/g, ''));
    } else {
      currentSection = { title: 'Analisis', items: [trimmed.replace(/\*\*/g, '')] };
    }
  }

  if (currentSection && currentSection.items.length > 0) {
    sections.push(currentSection);
  }

  return sections;
}
