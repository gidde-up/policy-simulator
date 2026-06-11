import React, { useState } from 'react';
import { GraduationCap } from 'lucide-react';

const STORAGE_KEY = 'policy-sim-first-visit-dismissed-v1';

function FirstVisitModal() {
  const [open, setOpen] = useState(() => {
    try {
      return !localStorage.getItem(STORAGE_KEY);
    } catch {
      return false;
    }
  });

  const dismiss = () => {
    try { localStorage.setItem(STORAGE_KEY, '1'); } catch { /* ignore */ }
    setOpen(false);
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
         role="dialog" aria-modal="true" aria-label="Welcome">
      <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-blue-100 rounded-lg">
            <GraduationCap className="w-6 h-6 text-blue-700" />
          </div>
          <h2 className="text-lg font-bold text-gray-900">
            A learning tool, not a forecast
          </h2>
        </div>
        <div className="text-sm text-gray-700 space-y-3 mb-5">
          <p>
            This simulator illustrates <strong>how</strong> policy choices reach
            employment - the direction, the transmission channels and the rough
            magnitude - using each country's real 2022 production structure
            (OECD data).
          </p>
          <p>
            It deliberately does NOT predict the future: no prices, no dynamics,
            no supply constraints. Results are honest accounting, shown with
            their parameter ranges.
          </p>
          <p>
            Start with a <strong>Guided Tour</strong> scenario - each one walks
            you through what the result teaches - then move to Free Exploration.
          </p>
        </div>
        <button
          onClick={dismiss}
          className="w-full py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-800"
        >
          Start exploring
        </button>
      </div>
    </div>
  );
}

export default FirstVisitModal;
