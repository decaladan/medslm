import { useState, useRef, useCallback } from 'react';
import gsap from 'gsap';
import type { ModelStatus } from '../hooks/useModel';

interface MarkerDef {
  name: string;
  unit: string;
  refLow: number;
  refHigh: number;
  placeholder: string;
}

const MARKERS: MarkerDef[] = [
  { name: 'Glucosa', unit: 'mg/dL', refLow: 70, refHigh: 100, placeholder: '95' },
  { name: 'Colesterol Total', unit: 'mg/dL', refLow: 125, refHigh: 199, placeholder: '185' },
  { name: 'LDL', unit: 'mg/dL', refLow: 50, refHigh: 129, placeholder: '110' },
  { name: 'HDL', unit: 'mg/dL', refLow: 40, refHigh: 80, placeholder: '55' },
  { name: 'Trigliceridos', unit: 'mg/dL', refLow: 35, refHigh: 149, placeholder: '120' },
  { name: 'Hemoglobina', unit: 'g/dL', refLow: 12, refHigh: 17, placeholder: '14.5' },
  { name: 'Leucocitos', unit: '/uL', refLow: 4500, refHigh: 11000, placeholder: '7200' },
  { name: 'Plaquetas', unit: '/uL', refLow: 150000, refHigh: 400000, placeholder: '250000' },
  { name: 'Hierro serico', unit: 'ug/dL', refLow: 60, refHigh: 170, placeholder: '90' },
  { name: 'Ferritina', unit: 'ng/mL', refLow: 20, refHigh: 250, placeholder: '80' },
  { name: 'Vitamina B12', unit: 'pg/mL', refLow: 200, refHigh: 900, placeholder: '450' },
  { name: 'Vitamina D', unit: 'ng/mL', refLow: 30, refHigh: 100, placeholder: '35' },
  { name: 'TSH', unit: 'mUI/L', refLow: 0.4, refHigh: 4.0, placeholder: '2.1' },
  { name: 'Creatinina', unit: 'mg/dL', refLow: 0.7, refHigh: 1.3, placeholder: '0.9' },
  { name: 'Acido urico', unit: 'mg/dL', refLow: 3.5, refHigh: 7.2, placeholder: '5.5' },
  { name: 'ALT (GPT)', unit: 'U/L', refLow: 7, refHigh: 56, placeholder: '25' },
  { name: 'AST (GOT)', unit: 'U/L', refLow: 10, refHigh: 40, placeholder: '22' },
  { name: 'GGT', unit: 'U/L', refLow: 9, refHigh: 48, placeholder: '30' },
];

function getStatus(value: number, refLow: number, refHigh: number): 'low' | 'normal' | 'high' {
  if (value < refLow) return 'low';
  if (value > refHigh) return 'high';
  return 'normal';
}

const DOT_COLORS = {
  low: 'bg-blue-500',
  normal: 'bg-emerald-500',
  high: 'bg-[#ff6600]',
};

function formatValue(val: number, marker: MarkerDef): string {
  if (marker.unit === '/uL' && val > 1000) return String(Math.round(val));
  if (val >= 100) return String(Math.round(val));
  return String(Math.round(val * 10) / 10);
}

interface BloodTestFormProps {
  status: ModelStatus;
  onGenerate: (prompt: string, maxTokens: number, temperature: number) => void;
}

export function BloodTestForm({ status, onGenerate }: BloodTestFormProps) {
  const [values, setValues] = useState<Record<string, string>>({});
  const [sex, setSex] = useState<'Hombre' | 'Mujer'>('Hombre');
  const [age, setAge] = useState('35');
  const [animating, setAnimating] = useState(false);
  const cardRefs = useRef<Record<string, HTMLDivElement | null>>({});

  const filledMarkers = MARKERS.filter((m) => values[m.name] && values[m.name].trim() !== '');
  const canGenerate = status === 'ready' && filledMarkers.length > 0;

  const handleSubmit = () => {
    if (!canGenerate) return;
    const lines = [`Paciente: ${sex}, ${age} anos.`, 'Resultados de analitica de sangre:', ''];
    for (const marker of filledMarkers) {
      const val = parseFloat(values[marker.name]);
      const st = getStatus(val, marker.refLow, marker.refHigh);
      const label = st === 'high' ? 'ALTO' : st === 'low' ? 'BAJO' : 'Normal';
      lines.push(`- ${marker.name}: ${val} ${marker.unit} [${label}] (ref: ${marker.refLow}-${marker.refHigh})`);
    }
    lines.push('');
    lines.push('Analiza los valores alterados y dame recomendaciones de dieta y estilo de vida en español.');
    onGenerate(lines.join('\n'), 2048, 0.7);
  };

  const animateValues = useCallback((targetValues: Record<string, string>) => {
    setAnimating(true);
    setValues({});

    const entries = Object.entries(targetValues);
    const tweenObj: Record<string, number> = {};
    const targetObj: Record<string, number> = {};
    entries.forEach(([key, val]) => {
      tweenObj[key] = 0;
      targetObj[key] = parseFloat(val);
    });

    const markerMap: Record<string, MarkerDef> = {};
    MARKERS.forEach((m) => { markerMap[m.name] = m; });

    gsap.to(tweenObj, {
      ...targetObj,
      duration: 0.8,
      ease: 'power2.out',
      stagger: { amount: 0.3, from: 'random' },
      onUpdate: () => {
        const intermediate: Record<string, string> = {};
        entries.forEach(([key]) => {
          const m = markerMap[key];
          if (m) intermediate[key] = formatValue(tweenObj[key], m);
        });
        setValues(intermediate);
      },
      onComplete: () => {
        setValues(targetValues);
        setAnimating(false);
        entries.forEach(([key, val]) => {
          const m = markerMap[key];
          if (!m) return;
          const st = getStatus(parseFloat(val), m.refLow, m.refHigh);
          if (st !== 'normal' && cardRefs.current[key]) {
            gsap.fromTo(cardRefs.current[key], { scale: 1.03 }, { scale: 1, duration: 0.3, ease: 'back.out(2)' });
          }
        });
      },
    });
  }, []);

  const generateRandom = () => {
    const randomSex = Math.random() < 0.5 ? 'Hombre' : 'Mujer';
    const randomAge = Math.floor(Math.random() * 55) + 20;
    const count = Math.floor(Math.random() * 5) + 5;
    const shuffled = [...MARKERS].sort(() => Math.random() - 0.5);
    const picked = shuffled.slice(0, count);
    const newValues: Record<string, string> = {};
    for (const marker of picked) {
      const roll = Math.random();
      let val: number;
      if (roll < 0.5) val = marker.refLow + Math.random() * (marker.refHigh - marker.refLow);
      else if (roll < 0.8) val = marker.refHigh * (1 + Math.random() * 0.6);
      else val = marker.refLow * (0.6 + Math.random() * 0.3);
      newValues[marker.name] = formatValue(val, marker);
    }
    setSex(randomSex);
    setAge(String(randomAge));
    animateValues(newValues);
  };

  const loadExample = () => {
    setSex('Mujer');
    setAge('52');
    animateValues({
      'Glucosa': '142', 'Colesterol Total': '225', 'LDL': '165', 'HDL': '38',
      'Trigliceridos': '198', 'Hemoglobina': '11.2', 'Vitamina D': '18', 'TSH': '5.8',
    });
  };

  return (
    <div className="space-y-5">
      {/* Section Header */}
      <h2 className="text-xs font-mono font-bold uppercase tracking-[0.3em] text-gray-400">
        BLOOD MARKER INPUTS
      </h2>

      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <label className="text-[10px] font-mono font-bold uppercase text-gray-500">Sexo</label>
            <select value={sex} onChange={(e) => setSex(e.target.value as 'Hombre' | 'Mujer')}
              className="bg-white text-sm font-mono font-bold border-2 border-black px-2 md:px-3 py-1.5 focus:outline-none">
              <option value="Hombre">Hombre</option>
              <option value="Mujer">Mujer</option>
            </select>
          </div>
          <div className="flex items-center gap-1.5">
            <label className="text-[10px] font-mono font-bold uppercase text-gray-500">Edad</label>
            <input type="number" value={age} onChange={(e) => setAge(e.target.value)}
              className="w-14 md:w-16 bg-white text-sm font-mono font-bold border-2 border-black px-2 md:px-3 py-1.5 text-center focus:outline-none" />
          </div>
        </div>
        <div className="flex gap-2">
          <button onClick={generateRandom} disabled={animating}
            className="px-3 md:px-5 py-2 border-2 border-black text-[10px] md:text-xs font-bold uppercase tracking-wider hover:bg-black hover:text-white disabled:opacity-50 transition-colors">
            RANDOM
          </button>
          <button onClick={loadExample} disabled={animating}
            className="px-3 md:px-5 py-2 border-2 border-black text-[10px] md:text-xs font-bold uppercase tracking-wider hover:bg-black hover:text-white disabled:opacity-50 transition-colors">
            EJEMPLO
          </button>
          <button onClick={handleSubmit} disabled={!canGenerate || animating}
            className="px-4 md:px-8 py-2 bg-[#ff6600] text-white text-[10px] md:text-xs font-bold uppercase tracking-wider border-2 border-[#ff6600] hover:bg-[#e55b00] hover:border-[#e55b00] disabled:opacity-30 disabled:cursor-not-allowed transition-colors flex-1 sm:flex-initial">
            ANALYZE
          </button>
        </div>
      </div>

      {/* Markers grid — mockup style with numbered index + status dot */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {MARKERS.map((marker, idx) => {
          const val = values[marker.name];
          const numVal = parseFloat(val);
          const hasValue = val && val.trim() !== '' && !isNaN(numVal);
          const st = hasValue ? getStatus(numVal, marker.refLow, marker.refHigh) : null;

          return (
            <div
              key={marker.name}
              ref={(el) => { cardRefs.current[marker.name] = el; }}
              className="border-2 border-gray-300 bg-white rounded-xl p-4 relative transition-colors duration-300"
            >
              {/* Top row: index number + status dot */}
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono font-bold text-gray-300">{idx + 1}</span>
                <div className={`w-3 h-3 rounded-full ${
                  st ? DOT_COLORS[st] : 'bg-gray-200'
                }`} />
              </div>

              {/* Value — massive centered */}
              <div className="flex items-center justify-center py-2 md:py-3">
                <input
                  type="number"
                  step="any"
                  value={val || ''}
                  onChange={(e) => setValues({ ...values, [marker.name]: e.target.value })}
                  placeholder={marker.placeholder}
                  className="w-full bg-transparent text-[2rem] md:text-[3.5rem] font-black text-center focus:outline-none font-mono leading-none placeholder-gray-200 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                />
              </div>

              {/* Bottom: marker name + unit on one line */}
              <div className="text-center pt-2 border-t border-gray-100">
                <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">
                  {marker.name} <span className="font-normal">{marker.unit}</span>
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
