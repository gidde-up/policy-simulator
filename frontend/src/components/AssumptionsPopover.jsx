import React, { useState, useEffect } from 'react';
import { Info, X } from 'lucide-react';
import { getAssumptions } from '../services/api';

// which registry fields are relevant to each lever
const MPC = 'marginal_propensity_to_consume';   // financing offset parameter
const LEVER_FIELDS = {
  tariffs: ['import_demand_elasticity', 'own_price_demand_elasticity',
            'retaliation_share', 'retaliation_top_n'],
  support: [MPC],   // pure accounting; financing offset uses the MPC
  stimulus: [MPC],
  production_subsidy: ['own_price_demand_elasticity', MPC],
  wage_subsidy: ['own_price_demand_elasticity',
                 'conventional_construction_labour_share', MPC],
  investment_tax_incentive: ['investment_incentive_redundancy', MPC],
  public_investment: [MPC],
  public_works: ['eiip_labour_cost_share',
                 'conventional_construction_labour_share', MPC],
  direct_public_employment: [MPC],
  depreciation: ['export_supply_elasticity', 'own_price_demand_elasticity'],
};

// per-lever context: what it changes, whether it is fiscal, whether the
// financing mode applies (Workstream F.2)
const LEVER_META = {
  tariffs: { fiscal: false, financing: false, what: 'Raises import prices in the tariffed sector; works through import substitution, downstream input costs and consumer prices.' },
  support: { fiscal: true, financing: true, what: 'Government demand for the supported sector, routed through the input-output system.' },
  stimulus: { fiscal: true, financing: true, what: 'A demand injection spread through the chosen spending basket (household, government or investment).' },
  production_subsidy: { fiscal: true, financing: true, what: 'Lowers output prices in the subsidised sector, raising real incomes and downstream demand.' },
  wage_subsidy: { fiscal: true, financing: true, what: 'Lowers the labour-cost share of the subsidised sector.' },
  investment_tax_incentive: { fiscal: true, financing: true, what: 'Subsidises investment; the windfall share is investment that would have happened anyway.' },
  public_investment: { fiscal: true, financing: true, what: 'Investment spending allocated across sectors (broad GFCF mix or a chosen target).' },
  public_works: { fiscal: true, financing: true, what: 'Labour-based or conventional infrastructure programme, reported in job-years.' },
  direct_public_employment: { fiscal: true, financing: true, what: 'Direct public-service hiring; the budget splits into wages and operating costs.' },
  depreciation: { fiscal: false, financing: false, what: 'A stylised exogenous exchange-rate shock: export gains against import-cost and real-income losses.' },
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
  const meta = LEVER_META[lever];
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

          {meta && (
            <div className="mb-3 text-xs text-gray-700 bg-gray-50 rounded p-2">
              <p>{meta.what}</p>
              <p className="mt-1 text-gray-500">
                {meta.fiscal ? 'Fiscal lever' : 'Not a fiscal lever'}
                {' · '}
                {meta.financing
                  ? 'financing mode applies (default tax-financed; offset scaled by the MPC)'
                  : 'financing mode does not apply'}
              </p>
              <p className="mt-1 text-gray-500">
                Full detail: the Methodology tab (sections 7 and 8).
              </p>
            </div>
          )}

          {entries === null && (
            <p className="text-xs text-gray-600">Loading…</p>
          )}
          {entries !== null && relevant.length === 0 && (
            <p className="text-xs text-gray-600">
              {lever === 'support'
                ? 'No behavioural parameters: this lever is pure final-demand accounting through the input-output system. The financing offset is scaled by the MPC.'
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
