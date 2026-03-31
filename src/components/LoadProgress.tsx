import { useState, useEffect } from 'react';

const BLOOD_FACTS = [
  'Your body contains about 5 liters of blood, circulating through 100,000 km of blood vessels.',
  'Red blood cells live for about 120 days. Your body produces 2 million new ones every second.',
  'A single drop of blood contains about 5 million red blood cells.',
  'Blood makes up about 7-8% of your total body weight.',
  'It takes about 20 seconds for blood to circulate through the entire body.',
  'White blood cells make up only about 1% of your blood but are crucial for immunity.',
  'Platelets survive only 8-10 days before being replaced by new ones from bone marrow.',
  'Your heart pumps about 7,500 liters of blood every single day.',
  'Blood type O negative is the universal donor — it can be given to anyone.',
  'Hemoglobin gives blood its red color by binding to oxygen molecules.',
  'The liver filters about 1.4 liters of blood per minute.',
  'Vitamin D is technically a hormone, and most people are deficient without knowing it.',
  'Ferritin levels can drop long before hemoglobin shows signs of anemia.',
  'TSH is one of the most sensitive markers for thyroid dysfunction.',
  'HDL cholesterol is called "good" because it helps remove other forms of cholesterol.',
];

interface LoadProgressProps {
  progress: {
    file: string;
    loaded: number;
    total: number;
    progress: number;
  } | null;
  message: string;
}

export function LoadProgress({ progress, message }: LoadProgressProps) {
  const percent = progress?.progress ?? 0;
  const circumference = 2 * Math.PI * 90;
  const offset = circumference - (percent / 100) * circumference;

  const [factIndex, setFactIndex] = useState(0);
  const [fadeIn, setFadeIn] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      setFadeIn(false);
      setTimeout(() => {
        setFactIndex((prev) => (prev + 1) % BLOOD_FACTS.length);
        setFadeIn(true);
      }, 400);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] md:min-h-[70vh] text-center px-4">
      {/* Big fact on top — fixed height to prevent layout jumps */}
      <div className="max-w-2xl px-2 md:px-6 mb-8 md:mb-10 h-20 md:h-24 flex flex-col justify-center">
        <p className="font-mono text-[10px] text-gray-400 uppercase tracking-[0.4em] mb-2 md:mb-3">
          DID YOU KNOW?
        </p>
        <p
          className={`text-sm md:text-lg lg:text-xl font-bold leading-snug tracking-tight transition-all duration-400 ${
            fadeIn ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
          }`}
        >
          {BLOOD_FACTS[factIndex]}
        </p>
      </div>

      {/* Progress ring */}
      <div className="relative w-40 h-40 md:w-52 md:h-52 mb-6 md:mb-8">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 200 200">
          <circle
            cx="100" cy="100" r="90"
            fill="none" stroke="rgba(0,0,0,0.1)" strokeWidth="6"
          />
          <circle
            cx="100" cy="100" r="90"
            fill="none" stroke="#ff6600" strokeWidth="6"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="butt"
            className="transition-all duration-500"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-4xl md:text-5xl font-bold tracking-tighter">
            {Math.round(percent)}%
          </span>
        </div>
      </div>

      {/* Status */}
      <div className="space-y-1">
        <h2 className="text-base md:text-xl font-bold uppercase tracking-[0.3em]">
          DOWNLOADING MODEL
        </h2>
        <p className="font-mono text-[10px] md:text-xs text-gray-500">
          {message}
          {progress && ` — ${formatBytes(progress.loaded)} / ${formatBytes(progress.total)}`}
        </p>
      </div>
    </div>
  );
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + ' MB';
  return (bytes / 1073741824).toFixed(2) + ' GB';
}
