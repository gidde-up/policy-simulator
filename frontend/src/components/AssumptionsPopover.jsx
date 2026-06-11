import React, { useState, useEffect } from 'react';
import { Info, X } from 'lucide-react';
import { getAssumptions } from '../services/api';

// which registry fields are relevant to each lever
const LEVER_FIELDS = {
  tariffs: ['import_demand_elasticity', 'own_price_demand_elasticity',
            'retaliation_share', 'retaliation_top_n'],
  support: [],   // pure accounting; show data-substitution entries instead
  stimulus: ['fiscal_multiplier'],
};

function AssumptionsPopover({ lever, countryCode }) {
  const [open, setOpen] = useState(false);
  const [entries, setEntries] = useState(null);

  useEffect(() => {
    if (!open || entries) return;
    getAssumptions(countryCode)
      .then((reg) => setEntries(reg.entries || []))
      .catch(() => setEntries([]));
  }, [open, countryCode, entries]);

  // reload when country changes
  useEffect(() => { setEntries(null); }, [countryCode]);

  const fields = LEVER_FIELDS[lever] || [];
  const relevant = (entries || []).filter((e) =>
    fields.includes(e.field) ||
    (lever === 'support' && e.method !== 'authored_constant'));

  return (
    <span className="relative inline-block">
      <button
        onClick={() => setOpen(!open)}
        aria-label={`Assumptions behind the ${lever} lever`}
        className="p-1 rounded-full text-gray-500 hover:text-blue-700 hover:bg-blue-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
      >
        <Info className="w-4 h-4" />
      </button>

      {open && (
        <div className="absolute right-0 z-20 mt-1 w-96 max-h-96 overflow-y-auto bg-white border border-gray-300 rounded-lg shadow-xl p-4 text-left">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-bold text-gray-800">
              Assumptions used by this lever
            </h4>
            <button onClick={() => setOpen(false)} aria-label="Close"
                    className="text-gray-500 hover:text-gray-700">
              <X className="w-4 h-4" />
            </button>
          </div>

          {entries === null && (
            <p className="text-xs text-gray-600">Loading…</p>
          )}
          {entries !== null && relevant.length === 0 && (
            <p className="text-xs text-gray-600">
              {lever === 'support'
                ? 'No behavioural parameters: this lever is pure final-demand accounting through the input-output system. The financing drag is the spending amount itself.'
                : 'No registry entries found.'}
            </p>
          )}

          {relevant.map((e) => (
            <div key={e.id} className="mb-3 pb-3 border-b border-gray-100 last:border-0">
              <div className="flex justify-between text-xs">
                <span className="font-mono text-gray-700">{e.id}</span>
                <span className="font-bold text-gray-900">{e.value}{e.unit === 'ratio' || e.unit === 'elasticity' ? '' : ` ${e.unit}`}</span>
              </div>
              {e.basis && (
                <p className="text-xs text-gray-700 mt-1">{e.basis}</p>
              )}
              {e.citation && (
                <p className="text-xs text-gray-500 mt-1 italic">{e.citation}</p>
              )}
            </div>
          ))}

          <p className="text-xs text-gray-500 mt-1">
            Full registry: backend/app/data/assumptions.json
          </p>
        </div>
      )}
    </span>
  );
}

export default AssumptionsPopover;
