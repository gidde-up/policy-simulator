import React, { useState, useEffect, useCallback } from 'react';
import { ChevronLeft, ChevronRight, Compass, ExternalLink, Play } from 'lucide-react';
import { getPresets, runSimulation } from '../services/api';
import ResultsPanel from './ResultsPanel';

function GuidedMode({ countryCode, onOpenInExplorer }) {
  const [scenarios, setScenarios] = useState([]);
  const [loadError, setLoadError] = useState(false);
  const [selected, setSelected] = useState(null);
  const [results, setResults] = useState(null);
  const [running, setRunning] = useState(false);
  const [step, setStep] = useState(0);

  useEffect(() => {
    setSelected(null);
    setResults(null);
    setStep(0);
    getPresets(countryCode)
      .then((d) => { setScenarios(d.presets || []); setLoadError(false); })
      .catch(() => { setScenarios([]); setLoadError(true); });
  }, [countryCode]);

  const runScenario = useCallback(async (scenario) => {
    setSelected(scenario);
    setStep(0);
    setRunning(true);
    setResults(null);
    try {
      const r = await runSimulation(scenario.params);
      setResults(r);
    } catch (err) {
      console.error('Scenario failed:', err);
      setResults(null);
    } finally {
      setRunning(false);
    }
  }, []);

  const steps = selected?.walkthrough || [];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Scenario picker */}
      <div className="lg:col-span-1">
        <div className="bg-white rounded-xl shadow-md p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Compass className="w-5 h-5 text-blue-700" />
            <h2 className="font-bold text-gray-900">Guided scenarios</h2>
          </div>
          <p className="text-sm text-gray-700 mb-4">
            Each scenario runs the model and walks you through what the
            result teaches. Every claim in the walkthroughs is enforced by
            automated tests against the model output.
          </p>

          {loadError && (
            <p className="text-sm text-amber-700">
              Scenarios could not be loaded from the server.
            </p>
          )}

          <div className="space-y-2">
            {scenarios.map((s) => (
              <button
                key={s.id}
                onClick={() => runScenario(s)}
                className={`w-full text-left p-3 rounded-lg border transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600
                  ${selected?.id === s.id
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-400'}`}
              >
                <div className="font-medium text-gray-900">{s.name}</div>
                <div className="text-xs text-gray-600 mt-0.5">{s.description}</div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Walkthrough + results */}
      <div className="lg:col-span-2 space-y-4">
        {!selected && !running && (
          <div className="bg-white rounded-xl shadow-md p-10 text-center text-gray-600">
            <Compass className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p className="font-medium text-gray-800">Pick a scenario on the left</p>
            <p className="text-sm mt-1">
              The model runs immediately and the walkthrough explains the result.
            </p>
          </div>
        )}

        {selected && steps.length > 0 && (
          <div className="bg-blue-900 text-white rounded-xl shadow-md p-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs uppercase tracking-wide text-blue-200">
                Walkthrough - step {step + 1} of {steps.length}
              </span>
              <div className="flex items-center space-x-1">
                <button
                  onClick={() => setStep(Math.max(0, step - 1))}
                  disabled={step === 0}
                  aria-label="Previous step"
                  className="p-1.5 rounded hover:bg-white/10 disabled:opacity-30 focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button
                  onClick={() => setStep(Math.min(steps.length - 1, step + 1))}
                  disabled={step >= steps.length - 1}
                  aria-label="Next step"
                  className="p-1.5 rounded hover:bg-white/10 disabled:opacity-30 focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
            <h3 className="text-lg font-bold mb-1">{steps[step].title}</h3>
            <p className="text-sm text-blue-100 leading-relaxed">{steps[step].text}</p>

            <div className="mt-4 pt-3 border-t border-white/20 flex items-center justify-between">
              <span className="text-xs text-blue-200">
                Lever settings: {summariseParams(selected.params)}
              </span>
              <button
                onClick={() => onOpenInExplorer(selected.params)}
                className="flex items-center space-x-1 text-xs font-medium bg-white/10 hover:bg-white/20 rounded px-2 py-1.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                <span>Open in Free Exploration</span>
              </button>
            </div>
          </div>
        )}

        <ResultsPanel results={results} loading={running} />
      </div>
    </div>
  );
}

function summariseParams(p) {
  const parts = [];
  for (const [s, v] of Object.entries(p.tariff_changes || {})) {
    parts.push(`tariff ${s.replace(/_/g, ' ')} +${v}pp`);
  }
  for (const [s, v] of Object.entries(p.sector_support || {})) {
    parts.push(`support ${s.replace(/_/g, ' ')} ${v}%`);
  }
  if (p.sme_stimulus > 0) parts.push(`stimulus ${p.sme_stimulus}% GDP`);
  return parts.join(' · ') || 'none';
}

export default GuidedMode;
