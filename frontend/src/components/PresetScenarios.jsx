import React, { useState, useEffect } from 'react';
import { Bookmark, Play, ChevronRight, Factory, Users, Leaf, Building } from 'lucide-react';
import { getPresets } from '../services/api';

const PRESET_ICONS = {
  manufacturing: Factory,
  youth: Users,
  green: Leaf,
  textile: Factory,
  agro: Leaf,
  services: Building,
};

function PresetScenarios({ countryCode, onSelectPreset }) {
  const [presets, setPresets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPreset, setSelectedPreset] = useState(null);

  useEffect(() => {
    loadPresets();
  }, [countryCode]);

  const loadPresets = async () => {
    setLoading(true);
    try {
      const data = await getPresets(countryCode);
      setPresets(data);
    } catch (err) {
      console.error('Error loading presets:', err);
      // Use fallback presets
      setPresets(getFallbackPresets(countryCode));
    } finally {
      setLoading(false);
    }
  };

  const getFallbackPresets = (country) => {
    if (country === 'ZAF') {
      return [
        {
          id: 'zaf_manufacturing',
          name: 'Manufacturing Boost',
          description: 'Protect and develop domestic manufacturing through tariffs and subsidies',
          icon: 'manufacturing',
          params: {
            country_code: 'ZAF',
            tariff_changes: { manufacturing: 15, automotive: 20 },
            subsidy_changes: { manufacturing: 5 },
            sme_stimulus: 0.5,
            productivity_investment: 3,
            time_horizon: 'medium',
          },
        },
        {
          id: 'zaf_youth',
          name: 'Youth Employment',
          description: 'Focus on labor-intensive sectors for youth job creation',
          icon: 'youth',
          params: {
            country_code: 'ZAF',
            tariff_changes: {},
            subsidy_changes: { trade: 8, other_services: 10 },
            sme_stimulus: 2.0,
            productivity_investment: 0,
            time_horizon: 'short',
          },
        },
        {
          id: 'zaf_green',
          name: 'Green Transition',
          description: 'Support shift from mining to sustainable industries',
          icon: 'green',
          params: {
            country_code: 'ZAF',
            tariff_changes: { utilities: -5 },
            subsidy_changes: { utilities: 15, construction: 10 },
            sme_stimulus: 1.0,
            productivity_investment: 5,
            time_horizon: 'long',
          },
        },
      ];
    } else {
      return [
        {
          id: 'tun_textile',
          name: 'Textile Revival',
          description: 'Revive textile sector competitiveness with quality upgrading',
          icon: 'textile',
          params: {
            country_code: 'TUN',
            tariff_changes: { textiles: 12 },
            subsidy_changes: { textiles: 10 },
            sme_stimulus: 0.5,
            productivity_investment: 4,
            time_horizon: 'medium',
          },
        },
        {
          id: 'tun_agro',
          name: 'Agro-Processing',
          description: 'Develop food processing to add value to agriculture',
          icon: 'agro',
          params: {
            country_code: 'TUN',
            tariff_changes: { food_processing: 8 },
            subsidy_changes: { food_processing: 12, agriculture: 5 },
            sme_stimulus: 1.5,
            productivity_investment: 2,
            time_horizon: 'medium',
          },
        },
        {
          id: 'tun_services',
          name: 'Services Expansion',
          description: 'Expand tourism and business services',
          icon: 'services',
          params: {
            country_code: 'TUN',
            tariff_changes: {},
            subsidy_changes: { other_services: 10, transport: 5 },
            sme_stimulus: 2.5,
            productivity_investment: 1,
            time_horizon: 'short',
          },
        },
      ];
    }
  };

  const handlePresetClick = (preset) => {
    setSelectedPreset(preset.id);
  };

  const handleApply = (preset) => {
    onSelectPreset(preset.params);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-md p-4">
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-1/3"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-4">
      <div className="flex items-center space-x-2 mb-4">
        <Bookmark className="w-5 h-5 text-blue-600" />
        <h3 className="font-bold text-gray-800">Preset Scenarios</h3>
      </div>

      <p className="text-sm text-gray-500 mb-4">
        Quick-start with pre-configured policy packages
      </p>

      <div className="space-y-3">
        {presets.map((preset) => {
          const Icon = PRESET_ICONS[preset.icon] || Factory;
          const isSelected = selectedPreset === preset.id;

          return (
            <div
              key={preset.id}
              className={`
                border rounded-lg overflow-hidden transition-all cursor-pointer
                ${isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}
              `}
            >
              <div
                className="p-3 flex items-center justify-between"
                onClick={() => handlePresetClick(preset)}
              >
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${isSelected ? 'bg-blue-100' : 'bg-gray-100'}`}>
                    <Icon className={`w-5 h-5 ${isSelected ? 'text-blue-600' : 'text-gray-600'}`} />
                  </div>
                  <div>
                    <div className="font-medium text-gray-800">{preset.name}</div>
                    <div className="text-xs text-gray-500">{preset.description}</div>
                  </div>
                </div>
                <ChevronRight
                  className={`w-5 h-5 text-gray-400 transition-transform ${isSelected ? 'rotate-90' : ''}`}
                />
              </div>

              {isSelected && (
                <div className="px-3 pb-3 border-t border-blue-100">
                  <div className="mt-3 text-xs text-gray-600 space-y-1">
                    {preset.params.tariff_changes && Object.keys(preset.params.tariff_changes).length > 0 && (
                      <div>
                        <span className="font-medium">Tariffs:</span>{' '}
                        {Object.entries(preset.params.tariff_changes)
                          .map(([s, v]) => `${s.replace('_', ' ')} ${v > 0 ? '+' : ''}${v}%`)
                          .join(', ')}
                      </div>
                    )}
                    {preset.params.subsidy_changes && Object.keys(preset.params.subsidy_changes).length > 0 && (
                      <div>
                        <span className="font-medium">Subsidies:</span>{' '}
                        {Object.entries(preset.params.subsidy_changes)
                          .map(([s, v]) => `${s.replace('_', ' ')} +${v}%`)
                          .join(', ')}
                      </div>
                    )}
                    {preset.params.sme_stimulus > 0 && (
                      <div>
                        <span className="font-medium">SME Stimulus:</span> {preset.params.sme_stimulus}% GDP
                      </div>
                    )}
                    <div>
                      <span className="font-medium">Time Horizon:</span>{' '}
                      {preset.params.time_horizon === 'short' ? '1 Year' :
                       preset.params.time_horizon === 'medium' ? '3 Years' : '5 Years'}
                    </div>
                  </div>

                  <button
                    onClick={() => handleApply(preset)}
                    className="mt-3 w-full flex items-center justify-center space-x-2 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Play className="w-4 h-4" />
                    <span>Apply Scenario</span>
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default PresetScenarios;
