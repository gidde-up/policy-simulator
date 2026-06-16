import React, { useState, useCallback } from 'react';
import { Play, RotateCcw, Database, Settings, Info, Compass, BookOpen } from 'lucide-react';
import Header from './components/Header';
import PolicyControls from './components/PolicyControls';
import ResultsPanel from './components/ResultsPanel';
import CountryDashboard from './components/CountryDashboard';
import GuidedMode from './components/GuidedMode';
import FirstVisitModal from './components/FirstVisitModal';
import LimitationsPanel from './components/LimitationsPanel';
import NotInToolPanel, { NotInToolTeasers } from './components/NotInToolPanel';
import MethodologyPanel from './components/MethodologyPanel';
import { useSimulation } from './hooks/useSimulation';

function App() {
  const [selectedCountry, setSelectedCountry] = useState('ZAF');
  const [activeTab, setActiveTab] = useState('guided'); // guided | explore | data | methodology
  const [limitationsOpen, setLimitationsOpen] = useState(false);
  const [notInToolOpen, setNotInToolOpen] = useState(false);

  const {
    params,
    results,
    loading,
    error,
    updateParam,
    updateTariff,
    updateSupport,
    updateSectorMap,
    simulate,
    loadPreset,
    reset,
  } = useSimulation();

  const handleCountryChange = useCallback((country) => {
    setSelectedCountry(country);
    updateParam('country_code', country);
  }, [updateParam]);

  // Guided mode hands a scenario over to Free Exploration
  const handleOpenInExplorer = useCallback((presetParams) => {
    loadPreset(presetParams);
    setActiveTab('explore');
  }, [loadPreset]);

  const tabs = [
    { id: 'guided', label: 'Guided Tour', icon: Compass },
    { id: 'explore', label: 'Free Exploration', icon: Settings },
    { id: 'data', label: 'Country Data', icon: Database },
    { id: 'methodology', label: 'Methodology', icon: Info },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      <FirstVisitModal />
      <LimitationsPanel open={limitationsOpen} onClose={() => setLimitationsOpen(false)} />
      <NotInToolPanel open={notInToolOpen} onClose={() => setNotInToolOpen(false)} />

      <Header
        selectedCountry={selectedCountry}
        onCountryChange={handleCountryChange}
      />

      {/* Persistent didactic banner with the limitations panel trigger */}
      <div className="bg-blue-900 text-blue-100 text-xs py-1">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-center space-x-3">
          <span>Learning tool illustrating transmission channels of policy choices - not a forecast</span>
          <button
            onClick={() => setLimitationsOpen(true)}
            className="underline decoration-dotted hover:text-white focus:outline-none focus-visible:ring-1 focus-visible:ring-white rounded flex items-center space-x-1"
          >
            <BookOpen className="w-3 h-3" />
            <span>what the model can and cannot tell you</span>
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-1 overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center space-x-2 px-4 py-3 border-b-2 transition-colors whitespace-nowrap
                    focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600
                    ${activeTab === tab.id
                      ? 'border-blue-600 text-blue-700'
                      : 'border-transparent text-gray-600 hover:text-gray-800'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  <span className="font-medium">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Guided Tour (default) */}
        {activeTab === 'guided' && (
          <GuidedMode
            countryCode={selectedCountry}
            onOpenInExplorer={handleOpenInExplorer}
          />
        )}

        {/* Free Exploration */}
        {activeTab === 'explore' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Controls */}
            <div className="lg:col-span-1 space-y-4">
              <PolicyControls
                countryCode={selectedCountry}
                params={params}
                onUpdateTariff={updateTariff}
                onUpdateSupport={updateSupport}
                onUpdateSectorMap={updateSectorMap}
                onUpdateParam={updateParam}
              />

              <NotInToolTeasers onOpen={() => setNotInToolOpen(true)} />

              {/* Action Buttons */}
              <div className="flex space-x-3">
                <button
                  onClick={simulate}
                  disabled={loading}
                  className="flex-1 flex items-center justify-center space-x-2 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-800"
                >
                  {loading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Simulating...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      <span>Run Simulation</span>
                    </>
                  )}
                </button>
                <button
                  onClick={reset}
                  className="px-4 py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
                  title="Reset all parameters"
                >
                  <RotateCcw className="w-5 h-5" />
                </button>
              </div>

              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
                  {error}
                </div>
              )}
            </div>

            {/* Right Column - Results */}
            <div className="lg:col-span-2">
              <ResultsPanel results={results} loading={loading} />
            </div>
          </div>
        )}

        {/* Data Tab: the country dashboard renders the headline indicators
            and employment-by-sector first, then the labour-market context
            and data caveats, with the cross-country comparison chart last */}
        {activeTab === 'data' && (
          <CountryDashboard countryCode={selectedCountry} />
        )}

        {/* Methodology Tab */}
        {activeTab === 'methodology' && <MethodologyPanel />}
      </main>
    </div>
  );
}

export default App;
