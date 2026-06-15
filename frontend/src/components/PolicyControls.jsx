import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, Settings } from 'lucide-react';
import PolicySlider from './PolicySlider';
import AssumptionsPopover from './AssumptionsPopover';
import { getSectors } from '../services/api';

// sectors below this share of the country's gross output are greyed out:
// lever effects there produce meaningless decimals (e.g. Senegal's
// automotive sector, 0.01% of output)
const MICRO_SECTOR_THRESHOLD = 0.005;

const SECTOR_GROUPS = {
  primary: { label: 'Primary', sectors: ['agriculture', 'mining'], color: 'green' },
  manufacturing: { label: 'Manufacturing', sectors: ['manufacturing', 'textiles', 'automotive', 'food_processing', 'chemicals'], color: 'blue' },
  infrastructure: { label: 'Infrastructure & Utilities', sectors: ['construction', 'utilities'], color: 'orange' },
  services: { label: 'Services', sectors: ['trade', 'transport', 'finance', 'public_services', 'other_services'], color: 'purple' },
};

const SECTOR_LABELS = {
  agriculture: 'Agriculture', mining: 'Mining', manufacturing: 'General Manufacturing',
  textiles: 'Textiles & Apparel', automotive: 'Automotive', food_processing: 'Food Processing',
  chemicals: 'Chemicals', construction: 'Construction', utilities: 'Utilities (Energy, Water)',
  trade: 'Wholesale & Retail Trade', transport: 'Transport & Logistics', finance: 'Financial Services',
  public_services: 'Public Services', other_services: 'Other Services (Tourism, etc.)',
};

const SECTOR_OPTIONS = Object.keys(SECTOR_LABELS);

// the four policy groups; trade goes last and is collapsed by default
const POLICY_GROUPS = [
  { id: 'industrial', label: '1. Industrial & sectoral policy', open: true },
  { id: 'public', label: '2. Public investment & employment programmes', open: true },
  { id: 'macro', label: '3. Macro-fiscal', open: true },
  { id: 'trade', label: '4. Trade & exchange rate', open: false },
];

function PolicyControls({ countryCode, params, onUpdateTariff, onUpdateSupport,
                          onUpdateSectorMap, onUpdateParam }) {
  const [openGroups, setOpenGroups] = useState(
    Object.fromEntries(POLICY_GROUPS.map(g => [g.id, g.open])));
  const [openLever, setOpenLever] = useState({ sector_support: true });
  const [sectorInfo, setSectorInfo] = useState({});

  useEffect(() => {
    let alive = true;
    getSectors(countryCode)
      .then((data) => {
        if (!alive) return;
        const map = {};
        (data.sectors || []).forEach((s) => { map[s.id] = s; });
        setSectorInfo(map);
      })
      .catch(() => setSectorInfo({}));
    return () => { alive = false; };
  }, [countryCode]);

  const toggleGroup = (id) => setOpenGroups(p => ({ ...p, [id]: !p[id] }));
  const toggleLever = (id) => setOpenLever(p => ({ ...p, [id]: !p[id] }));

  const compositionTooltip = (sector) => {
    const info = sectorInfo[sector];
    if (!info || !info.icio_industries?.length) return undefined;
    return 'Contains (OECD ICIO industries): ' +
      info.icio_industries.map((i) => `${i.code} ${i.description}`).join('; ');
  };

  // a sector-based lever: 14 sliders grouped by sector family
  const SectorLever = ({ id, title, values, onChange, max, color, lever }) => (
    <div className="border border-gray-200 rounded-lg mb-2">
      <button onClick={() => toggleLever(id)}
        className="w-full flex items-center justify-between p-3 hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 rounded-lg">
        <span className="font-medium text-gray-800">{title}</span>
        <span className="flex items-center space-x-2">
          {lever && <AssumptionsPopover lever={lever} countryCode={countryCode} />}
          {openLever[id] ? <ChevronUp className="w-4 h-4 text-gray-500" />
                         : <ChevronDown className="w-4 h-4 text-gray-500" />}
        </span>
      </button>
      {openLever[id] && (
        <div className="px-3 pb-3">
          {Object.entries(SECTOR_GROUPS).map(([gk, g]) => (
            <div key={gk} className="mt-2">
              <div className="text-xs font-semibold text-gray-400 uppercase mb-1">{g.label}</div>
              {g.sectors.map((sector) => {
                const share = sectorInfo[sector]?.output_share;
                const isMicro = share !== undefined && share < MICRO_SECTOR_THRESHOLD;
                return (
                  <div key={sector} title={compositionTooltip(sector)}>
                    <PolicySlider
                      label={SECTOR_LABELS[sector]}
                      value={values[sector] || 0}
                      onChange={(v) => onChange(sector, v)}
                      min={0} max={max} color={color || g.color}
                      disabled={isMicro}
                      disabledNote="below 0.5% of this economy's output"
                    />
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      )}
    </div>
  );

  // a structured lever card (compact form)
  const LeverCard = ({ id, title, lever, children }) => (
    <div className="border border-gray-200 rounded-lg mb-2">
      <button onClick={() => toggleLever(id)}
        className="w-full flex items-center justify-between p-3 hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 rounded-lg">
        <span className="font-medium text-gray-800">{title}</span>
        <span className="flex items-center space-x-2">
          {lever && <AssumptionsPopover lever={lever} countryCode={countryCode} />}
          {openLever[id] ? <ChevronUp className="w-4 h-4 text-gray-500" />
                         : <ChevronDown className="w-4 h-4 text-gray-500" />}
        </span>
      </button>
      {openLever[id] && <div className="px-3 pb-3 space-y-2">{children}</div>}
    </div>
  );

  const numField = (label, value, onChange, { min = 0, max = 20, step = 0.5, unit = '% of GDP' } = {}) => (
    <label className="flex items-center justify-between text-sm text-gray-700">
      <span>{label}</span>
      <span className="flex items-center space-x-1">
        <input type="number" min={min} max={max} step={step} value={value}
          onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
          className="w-20 text-right px-1 py-0.5 border rounded focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600" />
        <span className="text-xs text-gray-500">{unit}</span>
      </span>
    </label>
  );

  const sectorSelect = (label, value, onChange) => (
    <label className="flex items-center justify-between text-sm text-gray-700">
      <span>{label}</span>
      <select value={value || ''} onChange={(e) => onChange(e.target.value || null)}
        className="border rounded px-1 py-0.5 text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600">
        <option value="">Broad (GFCF mix)</option>
        {SECTOR_OPTIONS.map(s => <option key={s} value={s}>{SECTOR_LABELS[s]}</option>)}
      </select>
    </label>
  );

  const obj = (key) => params[key] || {};
  const setObj = (key, patch) =>
    onUpdateParam(key, { ...(params[key] || {}), ...patch });

  const Group = ({ id, label, children }) => (
    <div className="bg-white rounded-xl shadow-md overflow-hidden mb-3">
      <button onClick={() => toggleGroup(id)}
        className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600">
        <span className="font-bold text-gray-800">{label}</span>
        {openGroups[id] ? <ChevronUp className="w-5 h-5 text-gray-500" />
                        : <ChevronDown className="w-5 h-5 text-gray-500" />}
      </button>
      {openGroups[id] && <div className="p-3">{children}</div>}
    </div>
  );

  return (
    <div>
      {/* 1. Industrial & sectoral policy */}
      <Group id="industrial" label={POLICY_GROUPS[0].label}>
        <SectorLever id="production_subsidy" title="Production subsidy"
          lever="production_subsidy" values={obj('production_subsidy')}
          onChange={(s, v) => onUpdateSectorMap('production_subsidy', s, v)}
          max={30} color="green" />
        <SectorLever id="wage_subsidy" title="Wage subsidy"
          lever="wage_subsidy" values={obj('wage_subsidy')}
          onChange={(s, v) => onUpdateSectorMap('wage_subsidy', s, v)}
          max={30} color="green" />
        <LeverCard id="investment_tax_incentive" title="Investment tax incentive"
          lever="investment_tax_incentive">
          <p className="text-xs text-gray-600">Set what the incentive costs and how
            much of investment cost it covers; the windfall (investment that would
            have happened anyway) is shown in the results.</p>
          {numField('Fiscal cost', params.investment_tax_incentive?.fiscal_cost_pct_gdp || 0,
            (v) => onUpdateParam('investment_tax_incentive',
              v > 0 ? { ...(params.investment_tax_incentive || { intensity: 30 }), fiscal_cost_pct_gdp: v } : null),
            { max: 10 })}
          {params.investment_tax_incentive && numField('Intensity', params.investment_tax_incentive.intensity || 30,
            (v) => setObj('investment_tax_incentive', { intensity: v }),
            { max: 100, unit: '% of cost' })}
          {params.investment_tax_incentive && sectorSelect('Target',
            params.investment_tax_incentive.target,
            (t) => setObj('investment_tax_incentive', { target: t }))}
        </LeverCard>
        <SectorLever id="sector_support" title="Sector support (government spending)"
          lever="support" values={obj('sector_support')}
          onChange={onUpdateSupport} max={20} color="green" />
      </Group>

      {/* 2. Public investment & employment programmes */}
      <Group id="public" label={POLICY_GROUPS[1].label}>
        <LeverCard id="public_investment" title="Public investment" lever="public_investment">
          {numField('Amount', params.public_investment?.amount_pct_gdp || 0,
            (v) => onUpdateParam('public_investment',
              v > 0 ? { ...(params.public_investment || {}), amount_pct_gdp: v } : null))}
          {params.public_investment && sectorSelect('Target',
            params.public_investment.target,
            (t) => setObj('public_investment', { target: t }))}
        </LeverCard>
        <LeverCard id="public_works" title="Public works / EIIP (job-years)" lever="public_works">
          {numField('Budget', params.public_works?.budget_pct_gdp || 0,
            (v) => onUpdateParam('public_works',
              v > 0 ? { ...(params.public_works || { method: 'labour_based' }), budget_pct_gdp: v } : null))}
          {params.public_works && (
            <label className="flex items-center justify-between text-sm text-gray-700">
              <span>Method</span>
              <select value={params.public_works.method || 'labour_based'}
                onChange={(e) => setObj('public_works', { method: e.target.value })}
                className="border rounded px-1 py-0.5 text-sm">
                <option value="labour_based">Labour-based (EIIP)</option>
                <option value="conventional">Conventional</option>
              </select>
            </label>
          )}
        </LeverCard>
        <LeverCard id="direct_public_employment" title="Direct public hiring (job-years)" lever="direct_public_employment">
          {numField('Budget', params.direct_public_employment?.budget_pct_gdp || 0,
            (v) => onUpdateParam('direct_public_employment',
              v > 0 ? { budget_pct_gdp: v } : null))}
        </LeverCard>
      </Group>

      {/* 3. Macro-fiscal */}
      <Group id="macro" label={POLICY_GROUPS[2].label}>
        <LeverCard id="sme_stimulus" title="SME / demand stimulus" lever="stimulus">
          {numField('Stimulus', params.sme_stimulus || 0,
            (v) => onUpdateParam('sme_stimulus', v), { max: 10, step: 0.1 })}
          <label className="flex items-center justify-between text-sm text-gray-700">
            <span>Composition</span>
            <select value={params.stimulus_target || 'household'}
              onChange={(e) => onUpdateParam('stimulus_target', e.target.value)}
              className="border rounded px-1 py-0.5 text-sm">
              <option value="household">Household transfer</option>
              <option value="government">Government consumption</option>
              <option value="investment">Public investment</option>
            </select>
          </label>
        </LeverCard>
      </Group>

      {/* 4. Trade & exchange rate (collapsed by default) */}
      <Group id="trade" label={POLICY_GROUPS[3].label}>
        <SectorLever id="tariff_changes" title="Import tariffs"
          lever="tariffs" values={obj('tariff_changes')}
          onChange={onUpdateTariff} max={30} color="blue" />
        <LeverCard id="depreciation" title="Exchange-rate depreciation (stylised)"
          lever="depreciation">
          {numField('Depreciation', params.depreciation || 0,
            (v) => onUpdateParam('depreciation', v), { max: 50, step: 1, unit: '%' })}
        </LeverCard>
      </Group>

      {/* Model options */}
      <div className="bg-white rounded-xl shadow-md p-4">
        <div className="flex items-center space-x-2 mb-3">
          <Settings className="w-5 h-5 text-gray-600" />
          <h3 className="font-medium text-gray-800">Model Options</h3>
        </div>
        <div className="space-y-3">
          <label className="flex items-start space-x-3 cursor-pointer">
            <input type="checkbox" className="mt-1" checked={params.include_type_ii}
              onChange={(e) => onUpdateParam('include_type_ii', e.target.checked)} />
            <span className="text-sm text-gray-700">
              <span className="font-medium">Include induced effects (Type II)</span><br />
              Upper-bound illustration; consumption propensity capped at 1.
            </span>
          </label>
          <label className="flex items-start space-x-3 cursor-pointer">
            <input type="checkbox" className="mt-1" checked={params.include_retaliation}
              onChange={(e) => onUpdateParam('include_retaliation', e.target.checked)} />
            <span className="text-sm text-gray-700">
              <span className="font-medium">Trade-partner retaliation (stylised)</span><br />
              Export demand falls in the top export sectors.
            </span>
          </label>
          <div className="text-sm text-gray-700">
            <label htmlFor="financing-mode" className="font-medium block mb-1">
              Financing of fiscal levers
            </label>
            <select id="financing-mode" value={params.financing_mode || 'tax_financed'}
              onChange={(e) => onUpdateParam('financing_mode', e.target.value)}
              className="w-full border rounded px-2 py-1 text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600">
              <option value="deficit">Deficit-financed, no immediate offset</option>
              <option value="tax_financed">Tax-financed, MPC-scaled offset (default)</option>
              <option value="full_crowding_out">Full crowding-out upper bound</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">
              How positive-cost fiscal levers are paid for. Tax-financed
              withdraws the consumed share of the cost from household spending;
              full crowding-out is a deliberately strong upper bound.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PolicyControls;
