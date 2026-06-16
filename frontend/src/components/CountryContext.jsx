import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { getCountryContext } from '../services/api';

// National informality and working-poverty context (ILOSTAT), plus a
// data-and-model caveats panel (Workstream F.3). Context only -- the
// national indicators are never attached to scenario results; sectoral
// informality is used only in the job-quality composition view.
function CountryContext({ countryCode }) {
  const [data, setData] = useState(null);
  const [caveatsOpen, setCaveatsOpen] = useState(false);

  useEffect(() => {
    let alive = true;
    getCountryContext(countryCode)
      .then((d) => { if (alive) setData(d || {}); })
      .catch(() => setData({}));
    return () => { alive = false; };
  }, [countryCode]);

  if (!data) return null;
  const ctx = data.context || {};
  const caveats = data.caveats || null;
  const inf = ctx.national_informal_employment_rate_pct;
  const wp = ctx.working_poverty_rate_pct;
  if (inf == null && wp == null && !caveats) return null;

  const fmtPct = (v) => (v == null ? null : `${Math.round(v)}%`);

  return (
    <div className="space-y-4">
      {(inf != null || wp != null) && (
        <div className="bg-white rounded-xl shadow-md p-4">
          <h3 className="font-bold text-gray-800 mb-2">Labour-market context (ILOSTAT)</h3>
          <div className="grid grid-cols-2 gap-3 text-center">
            {inf != null && (
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500">Informal employment</div>
                <div className="text-2xl font-bold text-gray-800">{inf}%</div>
                <div className="text-xs text-gray-400">{ctx.national_informality_year}</div>
              </div>
            )}
            {wp != null && (
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500">Working poverty</div>
                <div className="text-2xl font-bold text-gray-800">{wp}%</div>
                <div className="text-xs text-gray-400">{ctx.working_poverty_year}</div>
              </div>
            )}
          </div>
          {ctx.data_mode && (
            <p className="text-xs text-gray-500 mt-2">
              Source: {ctx.data_mode}
              {ctx.national_informality_source ? ` - informality: ${ctx.national_informality_source}` : ''}
            </p>
          )}
          <p className="text-xs text-gray-400 mt-2">
            Informality and working-poverty indicators provide labour-market
            context. Sectoral informality is also used in the job-quality
            composition view. The simulator does not model workers moving into
            or out of informality.
          </p>
        </div>
      )}

      {/* Data and model caveats for this country */}
      {caveats && (
        <div className="bg-white rounded-xl shadow-md p-4">
          <button
            onClick={() => setCaveatsOpen((o) => !o)}
            aria-expanded={caveatsOpen}
            className="w-full flex items-center justify-between focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 rounded"
          >
            <span className="font-bold text-gray-800">Data and model caveats for this country</span>
            {caveatsOpen ? <ChevronUp className="w-5 h-5 text-gray-500" />
                         : <ChevronDown className="w-5 h-5 text-gray-500" />}
          </button>

          {caveats.warnings && caveats.warnings.length > 0 && (
            <ul className="mt-2 space-y-1">
              {caveats.warnings.map((w, i) => (
                <li key={i} className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded p-2">
                  {w}
                </li>
              ))}
            </ul>
          )}

          {caveatsOpen && (
            <div className="mt-3 text-sm text-gray-700 space-y-1">
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1">
                <CaveatRow label="Input-output data" value={`${caveats.io_data || 'n/a'}${caveats.io_data_year ? `, ${caveats.io_data_year}` : ''}`} />
                <CaveatRow label="Employment data" value={caveats.employment_data} />
                <CaveatRow label="Compensation data" value={caveats.compensation_data} />
                <CaveatRow label="Informality indicator" value={caveats.informality_indicator ? `${caveats.informality_indicator}${caveats.informality_year ? ` (${caveats.informality_year})` : ''}` : 'not available'} />
                <CaveatRow label="Working-poverty year" value={caveats.working_poverty_year || 'not available'} />
                <CaveatRow label="Employment validation gap" value={caveats.employment_validation_gap_pct != null ? `${caveats.employment_validation_gap_pct >= 0 ? '+' : ''}${Math.round(caveats.employment_validation_gap_pct)}% vs ILOSTAT total` : 'n/a'} />
                <CaveatRow label="Financing MPC" value={caveats.financing_mpc_status} />
                <CaveatRow label="Type II closure" value={caveats.type_ii_propensity_capped ? 'consumption propensity capped at 1 (upper-bound)' : 'uncapped'} />
              </dl>
              {caveats.notes && caveats.notes.length > 0 && (
                <ul className="mt-2 list-disc list-inside text-xs text-gray-500 space-y-0.5">
                  {caveats.notes.map((n, i) => <li key={i}>{n}</li>)}
                </ul>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function CaveatRow({ label, value }) {
  return (
    <div>
      <dt className="text-xs text-gray-500">{label}</dt>
      <dd className="text-sm text-gray-800">{value || 'not available'}</dd>
    </div>
  );
}

export default CountryContext;
