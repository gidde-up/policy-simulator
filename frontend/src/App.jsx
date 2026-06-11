import React, { useState, useCallback } from 'react';
import { Play, RotateCcw, Database, Settings, Info, Compass, BookOpen } from 'lucide-react';
import Header from './components/Header';
import PolicyControls from './components/PolicyControls';
import ResultsPanel from './components/ResultsPanel';
import CountryDashboard from './components/CountryDashboard';
import GuidedMode from './components/GuidedMode';
import FirstVisitModal from './components/FirstVisitModal';
import LimitationsPanel from './components/LimitationsPanel';
import { useSimulation } from './hooks/useSimulation';

function App() {
  const [selectedCountry, setSelectedCountry] = useState('ZAF');
  const [activeTab, setActiveTab] = useState('guided'); // guided | explore | data | methodology
  const [limitationsOpen, setLimitationsOpen] = useState(false);

  const {
    params,
    results,
    loading,
    error,
    updateParam,
    updateTariff,
    updateSupport,
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
                onUpdateParam={updateParam}
              />

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

        {/* Data Tab */}
        {activeTab === 'data' && (
          <CountryDashboard countryCode={selectedCountry} />
        )}

        {/* Methodology Tab */}
        {activeTab === 'methodology' && (
          <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-md p-8 space-y-6 text-sm text-gray-700">
            <div>
              <h2 className="text-xl font-bold text-gray-800 mb-2">What this tool is</h2>
              <p>
                A didactic simulator: it illustrates the direction, transmission channels
                and rough magnitude of employment effects of policy choices in a
                demand-driven Leontief input-output framework. It is NOT a forecasting
                or decision-support tool.
              </p>
            </div>

            <div>
              <h2 className="text-xl font-bold text-gray-800 mb-2">Data</h2>
              <ul className="list-disc ml-5 space-y-1">
                <li>
                  Inter-industry structure, final demand, imports and value added:
                  <span className="font-medium"> OECD Inter-Country Input-Output (ICIO) tables,
                  2025 edition (rev. Jan 2026), reference year 2022</span>, aggregated from
                  50 ICIO industries to 14 didactic sectors by a committed, documented concordance
                  (hover a sector in the controls to see its composition).
                </li>
                <li>
                  Employment and labour compensation by industry:
                  <span className="font-medium"> OECD Trade in Employment (TiM) 2025</span>,
                  with documented ILOSTAT fallbacks. Every substituted cell is recorded in the
                  assumptions registry (the info buttons next to each lever).
                </li>
                <li>
                  Dashboard indicators: World Bank WDI (live API). WDI GDP and labour-force
                  figures use different concepts and vintages than the ICIO-derived model
                  baseline; small discrepancies are expected.
                </li>
              </ul>
            </div>

            <div>
              <h2 className="text-xl font-bold text-gray-800 mb-2">Model core</h2>
              <p>
                Employment effects are computed as &#916;E = &ecirc; L &#916;F, where L is the
                Leontief inverse of the domestic coefficient matrix (Type I), or the
                Miyazawa household-endogenised inverse (Type II, optional toggle, labelled
                an upper bound because the consumption propensity is capped at 1; the sign
                of small net results can flip under that closure).
                Direct, indirect and induced components are reported separately.
                Results are comparative-static: one equilibrium adjustment, no time path.
              </p>
            </div>

            <div>
              <h2 className="text-xl font-bold text-gray-800 mb-2">Policy levers and channels</h2>
              <ul className="list-disc ml-5 space-y-1">
                <li>
                  <span className="font-medium">Tariffs</span>: four channels shown separately -
                  import substitution into the protected sector (bounded by the sector's
                  data-derived domestic absorption share); downstream input-cost push through
                  the price-side Leontief model; a real-income loss to households; and an
                  optional stylised retaliation toggle.
                </li>
                <li>
                  <span className="font-medium">Sector support</span>: a final-demand injection
                  with a financing-drag toggle (tax-financed, default on). The recurring lesson:
                  a tax-financed injection creates net jobs only when the supported sector
                  employs more people per dollar than the household consumption basket the
                  taxes crowd out.
                </li>
                <li>
                  <span className="font-medium">SME / demand stimulus</span>: spread through
                  household consumption, scaled by a cited first-round fiscal multiplier.
                </li>
              </ul>
              <p className="mt-2">
                All behavioural parameters carry full citations in the assumptions registry
                and are reported with ranges; results are never shown as a single point
                without their parameter range. Methodological notes per lever are in
                <code className="bg-gray-100 px-1 rounded text-xs"> docs/levers/</code>.
              </p>
            </div>

            <div>
              <h2 className="text-xl font-bold text-gray-800 mb-2">What the model cannot tell you</h2>
              <p>
                See the permanently accessible panel:{' '}
                <button
                  onClick={() => setLimitationsOpen(true)}
                  className="text-blue-700 underline focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 rounded"
                >
                  what the model can and cannot tell you
                </button>
                {' '}(also linked in the blue banner at the top).
              </p>
            </div>

            <div className="text-xs text-gray-500 border-t pt-4">
              Model v1.0.0 - OECD ICIO 2025 ed. (year 2022); employment: OECD TiM 2025 / ILOSTAT.
              Pipeline, validation reports and the assumptions registry are in the project repository.
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
