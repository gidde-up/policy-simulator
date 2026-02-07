import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Factory, Leaf, Building2, ShoppingBag, Truck, DollarSign, Zap } from 'lucide-react';
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
  onUpdateSubsidy,
  onUpdateParam,
}) {
  const [expandedGroups, setExpandedGroups] = useState({
    primary: false,
    manufacturing: true,
    infrastructure: false,
    services: false,
  });

  const [activeTab, setActiveTab] = useState('tariffs'); // 'tariffs' | 'subsidies' | 'other'

  const toggleGroup = (group) => {
    setExpandedGroups(prev => ({ ...prev, [group]: !prev[group] }));
  };

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
          onClick={() => setActiveTab('subsidies')}
          className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
            activeTab === 'subsidies'
              ? 'bg-green-50 text-green-700 border-b-2 border-green-500'
              : 'text-gray-500 hover:bg-gray-50'
          }`}
        >
          Subsidies
        </button>
        <button
          onClick={() => setActiveTab('other')}
          className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
            activeTab === 'other'
              ? 'bg-purple-50 text-purple-700 border-b-2 border-purple-500'
              : 'text-gray-500 hover:bg-gray-50'
          }`}
        >
          Other Policies
        </button>
      </div>

      <div className="p-4">
        {/* Tariffs Tab */}
        {activeTab === 'tariffs' && (
          <div>
            <p className="text-sm text-gray-600 mb-4">
              Adjust import tariff rates by sector. Higher tariffs protect domestic industries but may increase prices.
            </p>

            {Object.entries(SECTOR_GROUPS).map(([groupKey, group]) => {
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
                          value={params.tariff_changes[sector] || 0}
                          onChange={(val) => onUpdateTariff(sector, val)}
                          min={-20}
                          max={30}
                          color={group.color}
                          description={`Tariff rate change for ${SECTOR_LABELS[sector].toLowerCase()}`}
                        />
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Subsidies Tab */}
        {activeTab === 'subsidies' && (
          <div>
            <p className="text-sm text-gray-600 mb-4">
              Provide subsidies to support specific sectors. Subsidies can boost production but have fiscal costs.
            </p>

            {Object.entries(SECTOR_GROUPS).map(([groupKey, group]) => {
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
                    <div className="mt-2 pl-4 border-l-2 border-green-200">
                      {group.sectors.map((sector) => (
                        <PolicySlider
                          key={sector}
                          label={SECTOR_LABELS[sector]}
                          value={params.subsidy_changes[sector] || 0}
                          onChange={(val) => onUpdateSubsidy(sector, val)}
                          min={0}
                          max={20}
                          color="green"
                          description={`Subsidy support for ${SECTOR_LABELS[sector].toLowerCase()}`}
                        />
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Other Policies Tab */}
        {activeTab === 'other' && (
          <div className="space-y-6">
            {/* SME Stimulus */}
            <div className="p-4 bg-orange-50 rounded-lg">
              <div className="flex items-center space-x-2 mb-3">
                <DollarSign className="w-5 h-5 text-orange-600" />
                <h3 className="font-medium text-gray-800">SME Economic Stimulus</h3>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                Fiscal stimulus targeted at small and medium enterprises. SMEs are typically labor-intensive and create jobs in trade, services, and light manufacturing.
              </p>
              <PolicySlider
                label="SME Stimulus Package"
                value={params.sme_stimulus}
                onChange={(val) => onUpdateParam('sme_stimulus', val)}
                min={0}
                max={5}
                step={0.1}
                unit="% of GDP"
                color="orange"
              />
            </div>

            {/* Industrial Policy */}
            <div className="p-4 bg-purple-50 rounded-lg">
              <div className="flex items-center space-x-2 mb-3">
                <Zap className="w-5 h-5 text-purple-600" />
                <h3 className="font-medium text-gray-800">Industrial Policy & Productivity Investment</h3>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                Investment in industrial upgrading, technology adoption, and productivity improvement. May reduce jobs short-term but increases quality jobs long-term.
              </p>
              <PolicySlider
                label="Productivity Investment Target"
                value={params.productivity_investment}
                onChange={(val) => onUpdateParam('productivity_investment', val)}
                min={0}
                max={10}
                step={0.5}
                unit="%"
                color="purple"
              />
            </div>

          </div>
        )}
      </div>
    </div>
  );
}

export default PolicyControls;
