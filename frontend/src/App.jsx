import React, { useState, useCallback } from 'react';
import { Play, RotateCcw, BarChart3, MessageSquare, Database, Settings, Info, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import Header from './components/Header';
import PolicyControls from './components/PolicyControls';
import ResultsPanel from './components/ResultsPanel';
import SankeyDiagram from './components/SankeyDiagram';
import ChatPanel from './components/ChatPanel';
import CountryDashboard from './components/CountryDashboard';
import PresetScenarios from './components/PresetScenarios';
import { useSimulation } from './hooks/useSimulation';

function App() {
  const [selectedCountry, setSelectedCountry] = useState('ZAF');
  const [activeTab, setActiveTab] = useState('simulate'); // 'simulate' | 'data' | 'chat'

  const {
    params,
    results,
    loading,
    error,
    updateParam,
    updateTariff,
    updateSubsidy,
    simulate,
    loadPreset,
    reset,
  } = useSimulation();

  // Handle country change
  const handleCountryChange = useCallback((country) => {
    setSelectedCountry(country);
    updateParam('country_code', country);
  }, [updateParam]);

  // Handle preset selection
  const handlePresetSelect = useCallback((presetParams) => {
    loadPreset(presetParams);
  }, [loadPreset]);

  // Handle chat params application
  const handleChatParams = useCallback((chatParams) => {
    if (chatParams.country) {
      setSelectedCountry(chatParams.country);
    }
    loadPreset({
      country_code: chatParams.country || selectedCountry,
      tariff_changes: chatParams.tariff_changes || {},
      subsidy_changes: chatParams.subsidy_changes || {},
      sme_stimulus: chatParams.sme_stimulus || 0,
      productivity_investment: chatParams.productivity_investment || 0,
      time_horizon: chatParams.time_horizon === 1 ? 'short' :
                   chatParams.time_horizon === 5 ? 'long' : 'medium',
    });
  }, [loadPreset, selectedCountry]);

  const tabs = [
    { id: 'simulate', label: 'Policy Simulation', icon: Settings },
    { id: 'data', label: 'Country Data', icon: Database },
    { id: 'chat', label: 'AI Assistant', icon: MessageSquare },
    { id: 'methodology', label: 'Methodology', icon: Info },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      <Header
        selectedCountry={selectedCountry}
        onCountryChange={handleCountryChange}
      />

      {/* Tab Navigation */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center space-x-2 px-4 py-3 border-b-2 transition-colors
                    ${activeTab === tab.id
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
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
        {/* Simulation Tab */}
        {activeTab === 'simulate' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Controls */}
            <div className="lg:col-span-1 space-y-4">
              {/* Presets */}
              <PresetScenarios
                countryCode={selectedCountry}
                onSelectPreset={handlePresetSelect}
              />

              {/* Policy Controls */}
              <PolicyControls
                params={params}
                onUpdateTariff={updateTariff}
                onUpdateSubsidy={updateSubsidy}
                onUpdateParam={updateParam}
              />

              {/* Time Horizon Selector - Always Visible */}
              <div className="bg-white rounded-xl shadow-md p-4">
                <h3 className="font-medium text-gray-800 mb-3">Time Horizon</h3>
                <div className="flex space-x-2">
                  {[
                    { value: 'short', label: '1 Year', desc: 'Immediate effects' },
                    { value: 'medium', label: '3 Years', desc: 'Adjustment period' },
                    { value: 'long', label: '5 Years', desc: 'Structural change' },
                  ].map((option) => (
                    <button
                      key={option.value}
                      onClick={() => updateParam('time_horizon', option.value)}
                      className={`
                        flex-1 p-3 rounded-lg border-2 transition-all
                        ${params.time_horizon === option.value
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                        }
                      `}
                    >
                      <div className="font-medium text-gray-800">{option.label}</div>
                      <div className="text-xs text-gray-500">{option.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-3">
                <button
                  onClick={simulate}
                  disabled={loading}
                  className="flex-1 flex items-center justify-center space-x-2 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
                  className="px-4 py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 transition-colors"
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
            <div className="lg:col-span-2 space-y-4">
              <ResultsPanel results={results} loading={loading} />

              {results && (
                <SankeyDiagram transmissionPaths={results.transmission_paths} />
              )}
            </div>
          </div>
        )}

        {/* Data Tab */}
        {activeTab === 'data' && (
          <CountryDashboard countryCode={selectedCountry} />
        )}

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ChatPanel
              countryCode={selectedCountry}
              currentParams={params}
              onApplyParams={handleChatParams}
            />

            <div className="space-y-4">
              <div className="bg-white rounded-xl shadow-md p-6">
                <h3 className="font-bold text-gray-800 mb-4">Current Parameters</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Country:</span>
                    <span className="font-medium">
                      {{ 'ZAF': '🇿🇦 South Africa', 'TUN': '🇹🇳 Tunisia', 'VNM': '🇻🇳 Viet Nam', 'THA': '🇹🇭 Thailand' }[selectedCountry]}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Time Horizon:</span>
                    <span className="font-medium">
                      {params.time_horizon === 'short' ? '1 Year' :
                       params.time_horizon === 'medium' ? '3 Years' : '5 Years'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">SME Stimulus:</span>
                    <span className="font-medium">{params.sme_stimulus}% GDP</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Productivity Investment:</span>
                    <span className="font-medium">{params.productivity_investment}%</span>
                  </div>

                  {Object.keys(params.tariff_changes).length > 0 && (
                    <div>
                      <div className="text-gray-600 mb-1">Tariff Changes:</div>
                      <div className="pl-3 space-y-1">
                        {Object.entries(params.tariff_changes).map(([sector, value]) => (
                          <div key={sector} className="flex justify-between text-xs">
                            <span className="text-gray-500">{sector.replace('_', ' ')}</span>
                            <span className={value > 0 ? 'text-green-600' : 'text-red-600'}>
                              {value > 0 ? '+' : ''}{value}%
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {Object.keys(params.subsidy_changes).length > 0 && (
                    <div>
                      <div className="text-gray-600 mb-1">Subsidies:</div>
                      <div className="pl-3 space-y-1">
                        {Object.entries(params.subsidy_changes).map(([sector, value]) => (
                          <div key={sector} className="flex justify-between text-xs">
                            <span className="text-gray-500">{sector.replace('_', ' ')}</span>
                            <span className="text-green-600">+{value}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <button
                  onClick={simulate}
                  disabled={loading}
                  className="mt-4 w-full flex items-center justify-center space-x-2 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  <Play className="w-4 h-4" />
                  <span>Run Simulation</span>
                </button>
              </div>

              {results && (
                <div className="bg-white rounded-xl shadow-md p-6">
                  <h3 className="font-bold text-gray-800 mb-4">Quick Results</h3>
                  <div className={`text-center p-4 rounded-lg ${
                    results.aggregate.total_jobs > 0 ? 'bg-green-50' : 'bg-red-50'
                  }`}>
                    <div className={`text-3xl font-bold ${
                      results.aggregate.total_jobs > 0 ? 'text-green-700' : 'text-red-700'
                    }`}>
                      {results.aggregate.total_jobs > 0 ? '+' : ''}
                      {Math.round(results.aggregate.total_jobs).toLocaleString()}
                    </div>
                    <div className="text-gray-600">Total Jobs</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Methodology Tab */}
        {activeTab === 'methodology' && (
          <div className="max-w-4xl mx-auto space-y-6">
            {/* Important Disclaimer Banner */}
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
              <div className="flex items-start space-x-4">
                <AlertTriangle className="w-8 h-8 text-amber-600 flex-shrink-0 mt-1" />
                <div>
                  <h2 className="text-xl font-bold text-amber-800 mb-2">Important Disclaimer</h2>
                  <p className="text-amber-700">
                    This is an <strong>educational/didactic tool</strong> designed to help policymakers understand
                    the general mechanisms of how economic policies affect employment. The numerical results are
                    <strong> illustrative estimates</strong>, not precise forecasts, and should not be used as the
                    sole basis for actual policy decisions.
                  </p>
                </div>
              </div>
            </div>

            {/* Data Sources */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                <Database className="w-5 h-5 mr-2 text-blue-600" />
                Data Sources
              </h3>

              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-medium text-gray-800">Real Data (from World Bank WDI API)</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      Unemployment rates (total, youth, female, male), labor force size, GDP figures,
                      employment by sector, and population data are fetched in real-time from the
                      World Bank's World Development Indicators database.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-medium text-gray-800">Employment Multipliers - South Africa (OECD TiVA)</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      For <strong>South Africa</strong>, employment multipliers are derived from the OECD TiVA (Trade in Value Added)
                      database and ICIO (Inter-Country Input-Output) tables (2023 edition, reference year 2020).
                      These are research-grade estimates based on actual measured inter-industry linkages.
                      Demographic shares are from Stats SA Labour Force Survey.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <AlertTriangle className="w-5 h-5 text-amber-500 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-medium text-gray-800">Employment Multipliers - Tunisia (Stylized Estimates)</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      <strong>Tunisia</strong> is not covered by OECD ICIO. Employment multipliers for Tunisia are
                      stylized estimates based on regional patterns and ILO labor statistics.
                      These should be considered illustrative only.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <AlertTriangle className="w-5 h-5 text-amber-500 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-medium text-gray-800">Other Stylized Components</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      The following components still use simplified approximations:
                    </p>
                    <ul className="mt-2 space-y-2 text-sm text-gray-600">
                      <li className="flex items-start">
                        <span className="text-amber-500 mr-2">•</span>
                        <span><strong>Technical Coefficients Matrix:</strong> Inter-industry linkages use stylized estimates for both countries (not derived from national I-O tables).</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-amber-500 mr-2">•</span>
                        <span><strong>Sector GDP Shares:</strong> Approximate values that may differ from current official statistics.</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-amber-500 mr-2">•</span>
                        <span><strong>Policy Response Functions:</strong> Non-linear effects are stylized approximations, not econometrically estimated.</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            {/* Methodology */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                <Info className="w-5 h-5 mr-2 text-blue-600" />
                Model Methodology
              </h3>

              <div className="space-y-4 text-sm text-gray-600">
                <p>
                  This tool uses <strong>Leontief Input-Output analysis</strong>, a widely-used framework in economics
                  for understanding how changes in one sector ripple through an economy.
                </p>

                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-medium text-gray-800 mb-2">How It Works:</h4>
                  <ol className="list-decimal list-inside space-y-2">
                    <li><strong>Policy inputs</strong> (tariffs, subsidies, SME stimulus) are translated into demand changes in specific sectors</li>
                    <li>The <strong>Leontief inverse matrix</strong> calculates how demand changes propagate through supply chains</li>
                    <li><strong>Employment coefficients</strong> convert output changes to job effects</li>
                    <li>Results are disaggregated by <strong>direct</strong> (in targeted sectors), <strong>indirect</strong> (supply chain), and <strong>induced</strong> (consumer spending) effects</li>
                  </ol>
                </div>

                <div className="bg-blue-50 rounded-lg p-4">
                  <h4 className="font-medium text-blue-800 mb-2">Employment Multipliers:</h4>
                  <ul className="space-y-1">
                    <li><strong>Type I Multiplier:</strong> Direct + Indirect effects (within production system)</li>
                    <li><strong>Type II Multiplier:</strong> Type I + Induced effects (including household consumption)</li>
                  </ul>
                </div>

                <div className="bg-purple-50 rounded-lg p-4">
                  <h4 className="font-medium text-purple-800 mb-2">Non-Linear Policy Effects:</h4>
                  <p className="mb-2">The model incorporates realistic non-linear responses to policy changes:</p>
                  <ul className="space-y-2">
                    <li><strong>Tariffs:</strong> Positive effects peak around 8-12%. Above ~20%, negative effects dominate (trade retaliation, inefficiency, reduced export competitiveness). Very high tariffs can result in net job losses.</li>
                    <li><strong>Subsidies:</strong> Diminishing returns above 5%. High total subsidy commitments face fiscal crowding-out effects.</li>
                    <li><strong>SME Stimulus:</strong> Fiscal multiplier decreases at high levels (1.5 at 1% GDP, declining to ~1.0 at 4%+ GDP) due to absorption constraints.</li>
                    <li><strong>Policy Synergies:</strong> Balanced policy mixes (2-3 complementary instruments) are more effective than isolated interventions. Certain combinations provide bonuses (e.g., subsidies + productivity investment), while others may crowd out (e.g., very high tariffs + high subsidies).</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Limitations */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                <XCircle className="w-5 h-5 mr-2 text-red-500" />
                Known Limitations
              </h3>

              <ul className="space-y-3 text-sm text-gray-600">
                <li className="flex items-start">
                  <span className="text-red-500 mr-2 font-bold">1.</span>
                  <span><strong>Static model:</strong> Does not account for dynamic adjustments, behavioral responses, or general equilibrium effects over time.</span>
                </li>
                <li className="flex items-start">
                  <span className="text-amber-500 mr-2 font-bold">2.</span>
                  <span><strong>Simplified non-linearity:</strong> While the model includes diminishing returns and negative effects at extreme policy levels, these are stylized approximations rather than econometrically estimated response curves.</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-500 mr-2 font-bold">3.</span>
                  <span><strong>No price effects:</strong> Does not model how policy changes affect wages, prices, or exchange rates.</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-500 mr-2 font-bold">4.</span>
                  <span><strong>Simplified sectors:</strong> Uses 14 aggregated sectors; real economies have thousands of distinct industries.</span>
                </li>
                <li className="flex items-start">
                  <span className="text-amber-500 mr-2 font-bold">5.</span>
                  <span><strong>Stylized trade retaliation:</strong> High aggregate tariffs trigger a retaliation penalty, but this is a simplified approximation of complex trade dynamics.</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-500 mr-2 font-bold">6.</span>
                  <span><strong>No country-specific calibration:</strong> Non-linear thresholds and elasticities use generic values rather than country-specific empirical estimates.</span>
                </li>
              </ul>
            </div>

            {/* Appropriate Use */}
            <div className="bg-green-50 border border-green-200 rounded-xl p-6">
              <h3 className="text-lg font-bold text-green-800 mb-4 flex items-center">
                <CheckCircle className="w-5 h-5 mr-2" />
                Appropriate Use of This Tool
              </h3>

              <div className="grid md:grid-cols-2 gap-4 text-sm">
                <div>
                  <h4 className="font-medium text-green-700 mb-2">Good For:</h4>
                  <ul className="space-y-1 text-green-600">
                    <li>• Understanding policy transmission mechanisms</li>
                    <li>• Comparing relative effects of different policies</li>
                    <li>• Educational/training purposes</li>
                    <li>• Identifying which sectors are most affected</li>
                    <li>• Illustrating direct vs. indirect employment effects</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-red-700 mb-2">Not Suitable For:</h4>
                  <ul className="space-y-1 text-red-600">
                    <li>• Precise job creation forecasts</li>
                    <li>• Budget allocation decisions</li>
                    <li>• Official policy impact assessments</li>
                    <li>• Replacing comprehensive economic modeling</li>
                    <li>• Long-term structural predictions</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* For Better Estimates */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-lg font-bold text-gray-800 mb-4">For More Accurate Policy Analysis</h3>
              <p className="text-sm text-gray-600 mb-4">
                For actual policy decisions, we recommend using:
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  <span>Official national Input-Output tables from statistics offices</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  <span>OECD Inter-Country Input-Output (ICIO) database for actual multipliers</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  <span>Computable General Equilibrium (CGE) models for comprehensive analysis</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  <span>Country-specific labor market studies and econometric estimates</span>
                </li>
              </ul>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-8 py-6">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="text-sm text-gray-500">
              <p>Economic Policy Simulator - A didactic tool for understanding employment effects of policy choices</p>
              <p className="mt-1">Data sources: World Bank WDI (real-time) | Model: Stylized I-O matrices</p>
            </div>
            <div className="flex items-center space-x-4 text-sm text-gray-400">
              <button
                onClick={() => setActiveTab('methodology')}
                className="text-amber-600 hover:text-amber-700 font-medium"
              >
                View Methodology & Disclaimer
              </button>
              <span>|</span>
              <a href="https://data.worldbank.org" target="_blank" rel="noopener noreferrer" className="hover:text-blue-600">
                World Bank
              </a>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t text-center text-xs text-gray-400">
            <p>
              <span className="text-amber-600 font-medium">Educational tool only.</span> Results are illustrative estimates using simplified economic models.
              Not suitable for official policy decisions. See Methodology tab for details on data sources and limitations.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
