import { useState, useEffect } from 'react';
import { useModel } from './hooks/useModel';
import { BloodTestForm } from './components/BloodTestForm';
import { OutputPanel } from './components/OutputPanel';
import { LoadProgress } from './components/LoadProgress';
import { SceneBackground } from './components/SceneBackground';

const MODEL = {
  id: 'charlierun82/MedSLM-Qwen3-0.6B-Blood-ES',
  name: 'MedSLM 0.6B',
  size: '1.4GB',
  dtype: 'fp16',
};

type Screen = 'landing' | 'loading' | 'input' | 'analyzing' | 'results';

function App() {
  const {
    status,
    statusMessage,
    loadProgress,
    currentOutput,
    liveMetrics,
    metricsHistory,
    error,
    loadModel,
    generate,
  } = useModel();

  const [screen, setScreen] = useState<Screen>('landing');
  const [analyzedPrompt, setAnalyzedPrompt] = useState('');

  // Sync model status → screen transitions
  useEffect(() => {
    if (status === 'loading') setScreen('loading');
    if (status === 'ready' && screen === 'loading') setScreen('input');
    if (status === 'generating') setScreen('analyzing');
  }, [status, screen]);

  // When output arrives, switch to results
  useEffect(() => {
    if (currentOutput && currentOutput.trim().length > 0 && status === 'ready' && screen === 'analyzing') {
      setScreen('results');
    }
  }, [currentOutput, status, screen]);

  const handleGenerate = (prompt: string, maxTokens: number, temperature: number) => {
    setAnalyzedPrompt(prompt);
    generate(prompt, maxTokens, temperature);
  };

  const handleBackToInput = () => {
    setScreen('input');
  };

  return (
    <div className="min-h-screen p-4 md:p-6 relative">
      <SceneBackground />
      <div className="max-w-6xl mx-auto relative z-10">
        {/* Top Bar */}
        <header className="flex items-center justify-between mb-4 md:mb-6 pb-3 md:pb-4 border-b-2 border-black">
          <div className="flex items-center gap-2 md:gap-3">
            <div className="w-7 h-7 md:w-8 md:h-8 bg-black flex items-center justify-center">
              <span className="text-[#ff6600] font-mono font-bold text-base md:text-lg">M</span>
            </div>
            <span className="font-bold text-base md:text-lg tracking-tight">MEDSLM</span>
          </div>
          <div className="flex items-center gap-1.5 md:gap-3">
            {(screen === 'input' || screen === 'analyzing' || screen === 'results') && (
              <div className="flex items-center gap-1.5 px-2 md:px-3 py-1 border-2 border-green-600 text-green-700 text-[9px] md:text-xs font-mono font-bold uppercase">
                <div className="w-2 h-2 bg-green-500 rounded-full" />
                <span className="hidden sm:inline">MODEL </span>READY
              </div>
            )}
            <Badge label="PRIVATE" />
            <span className="hidden sm:inline"><Badge label="ON-DEVICE" /></span>
            <span className="hidden md:inline"><Badge label="WEBGPU" /></span>
          </div>
        </header>

        {/* Error */}
        {error && (
          <div className="border-2 border-red-500 p-4 mb-4">
            <p className="font-mono text-sm text-red-600">
              <strong>ERROR:</strong> {error}
            </p>
            <p className="font-mono text-xs text-gray-500 mt-1">
              WebGPU may not be supported. Try Chrome 113+ or Edge 113+.
            </p>
          </div>
        )}

        {/* SCREEN 1: Landing */}
        {screen === 'landing' && (
          <div className="flex flex-col items-center justify-center min-h-[60vh] md:min-h-[70vh] text-center space-y-6 md:space-y-8 px-2">
            <h1 className="text-[clamp(2.5rem,10vw,8rem)] font-bold leading-none tracking-tighter">
              MEDSLM
            </h1>
            <p className="font-mono text-xs md:text-sm text-gray-500 max-w-md">
              Private Blood Test Analysis powered by WebGPU.
              <br />
              {MODEL.size} model downloads to your browser and runs locally.
            </p>
            <button
              onClick={() => loadModel(MODEL.id, MODEL.dtype)}
              className="px-8 md:px-10 py-3 md:py-4 bg-[#ff6600] text-white font-bold text-base md:text-lg uppercase tracking-wider hover:bg-[#e55b00] transition-colors"
            >
              LOAD AI MODEL ↓
            </button>
            <div className="flex gap-2 md:gap-3 flex-wrap justify-center">
              <Badge label="PRIVATE" />
              <Badge label="ON-DEVICE" />
              <Badge label="ZERO DATA SENT" />
            </div>
          </div>
        )}

        {/* SCREEN 2: Loading */}
        {screen === 'loading' && (
          <LoadProgress progress={loadProgress} message={statusMessage} />
        )}

        {/* SCREEN 3: Blood Test Input */}
        {screen === 'input' && (
          <BloodTestForm status={status} onGenerate={handleGenerate} />
        )}

        {/* SCREEN 4: Analyzing / SCREEN 5: Results */}
        {(screen === 'analyzing' || screen === 'results') && (
          <OutputPanel
            output={currentOutput}
            status={status}
            liveMetrics={liveMetrics}
            metricsHistory={metricsHistory}
            onBack={handleBackToInput}
            analyzedPrompt={analyzedPrompt}
          />
        )}

        {/* Footer */}
        <footer className="mt-12 pt-4 border-t border-gray-300 text-center">
          <p className="font-mono text-[10px] text-gray-400 uppercase tracking-widest">
            LOCAL INFERENCE ON-DEVICE • MODEL v0.1 • SECURE • END-TO-END ENCRYPTION
          </p>
        </footer>
      </div>
    </div>
  );
}

function Badge({ label }: { label: string }) {
  return (
    <span className="px-2 py-1 border-2 border-black text-[10px] font-mono font-bold uppercase tracking-wider">
      {label}
    </span>
  );
}

export default App;
