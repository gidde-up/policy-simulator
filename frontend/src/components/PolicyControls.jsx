import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Factory, Leaf, Building2, ShoppingBag, DollarSign, Settings } from 'lucide-react';
import PolicySlider from './PolicySlider';

const SECTOR_GROUPS = {
  primary: {
    label: 'Primary Sectors',
    icon: Leaf,
    sectors: ['agriculture', 'mining'],
    color: 'green',
  },
  manufacturing: {
    label: 'Manufacturing',
    icon: Factory,
    sectors: ['manufacturing', 'textiles', 'automotive', 'food_processing', 'chemicals'],
    color: 'blue',
  },
  infrastructure: {
    label: 'Infrastructure & Utilities',
    icon: Building2,
    sectors: ['construction', 'utilities'],
    color: 'orange',
  },
  services: {
    label: 'Services',
    icon: ShoppingBag,
    sectors: ['trade', 'transport', 'finance', 'public_services', 'other_services'],
    color: 'purple',
  },
};

const SECTOR_LABELS = {
  agriculture: 'Agriculture',
  mining: 'Mining',
  manufacturing: 'General Manufacturing',
  textiles: 'Textiles & Apparel',
  automotive: 'Automotive',
  food_processing: 'Food Processing',
  chemicals: 'Chemicals',
  construction: 'Construction',
  utilities: 'Utilities (Energy, Water)',
  trade: 'Wholesale & Retail Trade',
  transport: 'Transport & Logistics',
  finance: 'Financial Services',
  public_services: 'Public Services',
  other_services: 'Other Services (Tourism, etc.)',
};

function PolicyControls({
  params,
  onUpdateTariff,
  onUpdateSupport,
  onUpdateParam,
}) {
  const [expandedGroups, setExpandedGroups] = useState({
    primary: false,
    manufacturing: true,
    infrastructure: false,
    services: false,
  });

  const [activeTab, setActiveTab] = useState('tariffs'); // 'tariffs' | 'support' | 'other'

  const toggleGroup = (group) => {
    setExpandedGroups(prev => ({ ...prev, [group]: !prev[group] }));
  };

  const renderSectorSliders = (values, onChange, { min, max, color, kind }) => (
    Object.entries(SECTOR_GROUPS).map(([groupKey, group]) => {
      const Icon = group.icon;
      return (
        <div key={groupKey} className="mb-3">
          <button
            onClick={() => toggleGroup(groupKey)}
            className="w-full flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-center space-x-2">
              <Icon className="w-5 h-5 text-gray-600" />
              <span className="font-medium text-gray-700">{group.label}</span>
            </div>
            {expandedGroups[groupKey] ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>

          {expandedGroups[groupKey] && (
            <div className="mt-2 pl-4 border-l-2 border-gray-200">
              {group.sectors.map((sector) => (
                <PolicySlider
                  key={sector}
                  label={SECTOR_LABELS[sector]}
                  value={values[sector] || 0}
                  onChange={(val) => onChange(sector, val)}
                  min={min}
                  max={max}
                  color={color || group.color}
                  description={`${kind} for ${SECTOR_LABELS[sector].toLowerCase()}`}
                />
              ))}
            </div>
          )}
        </div>
      );
    })
  );

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      {/* Tab Navigation */}
      <div className="flex border-b">
        <button
          onClick={() => setActiveTab('tariffs')}
          className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
            activeTab === 'tariffs'
              ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-500'
              : 'text-gray-500 hover:bg-gray-50'
          }`}
        >
          Import Tariffs
        </button>
        <button
          onClick={() => setActiveTab('support')}
          className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
            activeTab === 'support'
              ? 'bg-green-50 text-green-700 border-b-2 border-green-500'
              : 'text-gray-500 hover:bg-gray-50'
          }`}
        >
          Sector Support
        </button>
        <button
          onClick={() => setActiveTab('other')}
          className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
            activeTab === 'other'
              ? 'bg-purple-50 text-purple-700 border-b-2 border-purple-500'
              : 'text-gray-500 hover:bg-gray-50'
          }`}
        >
          Stimulus & Options
        </button>
      </div>

      <div className="p-4">
        {/* Tariffs Tab */}
        {activeTab === 'tariffs' && (
          <div>
            <p className="text-sm text-gray-600 mb-4">
              Raise import tariffs by sector. The model shows the protected-sector
              gain against downstream input-cost and real-income losses.
            </p>
            {renderSectorSliders(params.tariff_changes, onUpdateTariff,
              { min: 0, max: 30, kind: 'Tariff increase' })}
          </div>
        )}

        {/* Sector Support Tab */}
        {activeTab === 'support' && (
          <div>
            <p className="text-sm text-gray-600 mb-4">
              Government spending in support of a sector (as % of the sector's
              output). With the financing drag on, the same amount is taken out
              of household consumption (tax-financed).
            </p>
            {renderSectorSliders(params.sector_support, onUpdateSupport,
              { min: 0, max: 20, color: 'green', kind: 'Government support' })}
          </div>
        )}

        {/* Stimulus & Options Tab */}
        {activeTab === 'other' && (
          <div className="space-y-6">
            {/* SME Stimulus */}
            <div className="p-4 bg-orange-50 rounded-lg">
              <div className="flex items-center space-x-2 mb-3">
                <DollarSign className="w-5 h-5 text-orange-600" />
                <h3 className="font-medium text-gray-800">SME / Demand Stimulus</h3>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                Broad demand stimulus spread through household consumption
                patterns, scaled by a cited first-round fiscal multiplier.
              </p>
              <PolicySlider
                label="Stimulus Package"
                value={params.sme_stimulus}
                onChange={(val) => onUpdateParam('sme_stimulus', val)}
                min={0}
                max={5}
                step={0.1}
                unit="% of GDP"
                color="orange"
              />
            </div>

            {/* Model options */}
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-2 mb-3">
                <Settings className="w-5 h-5 text-gray-600" />
                <h3 className="font-medium text-gray-800">Model Options</h3>
              </div>
              <div className="space-y-3">
                <label className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    className="mt-1"
                    checked={params.include_type_ii}
                    onChange={(e) => onUpdateParam('include_type_ii', e.target.checked)}
                  />
                  <span className="text-sm text-gray-700">
                    <span className="font-medium">Include induced effects (Type II)</span><br />
                    Upper-bound illustration: household spending of labour income
                    is recycled, with the consumption propensity capped at 1.
                  </span>
                </label>
                <label className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    className="mt-1"
                    checked={params.include_retaliation}
                    onChange={(e) => onUpdateParam('include_retaliation', e.target.checked)}
                  />
                  <span className="text-sm text-gray-700">
                    <span className="font-medium">Trade-partner retaliation (stylised)</span><br />
                    Export demand falls in the top export sectors, mirroring the
                    2018-19 trade-war episode.
                  </span>
                </label>
                <label className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    className="mt-1"
                    checked={params.include_financing_drag}
                    onChange={(e) => onUpdateParam('include_financing_drag', e.target.checked)}
                  />
                  <span className="text-sm text-gray-700">
                    <span className="font-medium">Financing drag on sector support</span><br />
                    Tax-financed spending: the support amount is subtracted from
                    household consumption, showing net rather than gross effects.
                  </span>
                </label>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default PolicyControls;
