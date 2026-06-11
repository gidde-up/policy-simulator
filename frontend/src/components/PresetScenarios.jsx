import React, { useState, useEffect } from 'react';
import { Bookmark, Play, ChevronRight, Factory, Leaf, Building, DollarSign } from 'lucide-react';
import { getPresets } from '../services/api';

// icon picked from the preset id keywords; purely decorative
function presetIcon(id) {
  if (/agri|food|rural/.test(id)) return Leaf;
  if (/construction|services|trade|demand|stimulus/.test(id)) return Building;
  if (/stimulus|demand/.test(id)) return DollarSign;
  return Factory;
}

function PresetScenarios({ countryCode, onSelectPreset }) {
  const [presets, setPresets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState(null);

  useEffect(() => {
    loadPresets();
  }, [countryCode]);

  const loadPresets = async () => {
    setLoading(true);
    setLoadError(false);
    try {
      const data = await getPresets(countryCode);
      setPresets(data.presets || []);
    } catch (err) {
      console.error('Error loading presets:', err);
      setPresets([]);
      setLoadError(true);
    } finally {
      setLoading(false);
    }
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

      {loadError && (
        <p className="text-sm text-amber-600">
          Presets could not be loaded from the server.
        </p>
      )}
      {!loadError && presets.length === 0 && (
        <p className="text-sm text-gray-500">
          No presets available for this country yet.
        </p>
      )}

      <div className="space-y-3">
        {presets.map((preset) => {
          const Icon = presetIcon(preset.id);
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
                onClick={() => setSelectedPreset(preset.id)}
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
                          .map(([s, v]) => `${s.replace('_', ' ')} +${v}pp`)
                          .join(', ')}
                      </div>
                    )}
                    {preset.params.sector_support && Object.keys(preset.params.sector_support).length > 0 && (
                      <div>
                        <span className="font-medium">Sector support:</span>{' '}
                        {Object.entries(preset.params.sector_support)
                          .map(([s, v]) => `${s.replace('_', ' ')} +${v}%`)
                          .join(', ')}
                      </div>
                    )}
                    {preset.params.sme_stimulus > 0 && (
                      <div>
                        <span className="font-medium">Demand stimulus:</span> {preset.params.sme_stimulus}% of GDP
                      </div>
                    )}
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
