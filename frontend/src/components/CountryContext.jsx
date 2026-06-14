import React, { useState, useEffect } from 'react';
import { getCountryContext } from '../services/api';

// National informality and working-poverty context (ILOSTAT). Context
// only -- never attached to scenario results.
function CountryContext({ countryCode }) {
  const [ctx, setCtx] = useState(null);

  useEffect(() => {
    let alive = true;
    getCountryContext(countryCode)
      .then((d) => { if (alive) setCtx(d.context || {}); })
      .catch(() => setCtx({}));
    return () => { alive = false; };
  }, [countryCode]);

  if (!ctx) return null;
  const inf = ctx.national_informal_employment_rate_pct;
  const wp = ctx.working_poverty_rate_pct;
  if (inf == null && wp == null) return null;

  return (
    <div className="bg-white rounded-xl shadow-md p-4 mb-4">
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
      <p className="text-xs text-gray-400 mt-2">
        National context indicators only - not attached to scenario results
        (no sector-level data exists).
      </p>
    </div>
  );
}

export default CountryContext;
