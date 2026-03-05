import React, { useState, useCallback } from 'react';
import { Play, RotateCcw, BarChart3, MessageSquare, Database, Settings, Info, AlertTriangle, CheckCircle, XCircle, FileText, ChevronDown, ChevronUp } from 'lucide-react';
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
  const [showTechnicalDocs, setShowTechnicalDocs] = useState(false);

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
                    <li><strong>SME Stimulus:</strong> Fiscal multiplier 1.0 at 1% GDP, declining to ~0.75 at 3%+ GDP (IMF/World Bank developing-country estimates). Absorption constraints limit effectiveness at high levels.</li>
                    <li><strong>Productivity Investment:</strong> Short-term effect is slightly negative (displacement dominates, −0.15×); positive effects emerge at medium (3yr, +0.45×) and long term (5yr, +1.0×) via competitiveness gains.</li>
                    <li><strong>Policy Synergies:</strong> Balanced mixes (2-3 instruments) receive a modest bonus (up to 1.08×). High tariffs combined with high subsidies trigger a rent-seeking penalty rather than a synergy bonus.</li>
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

            {/* Full Technical Documentation */}
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <button
                onClick={() => setShowTechnicalDocs(!showTechnicalDocs)}
                className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-gray-600" />
                  <h3 className="text-lg font-bold text-gray-800">Full Technical Model Documentation</h3>
                </div>
                {showTechnicalDocs ? (
                  <ChevronUp className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                )}
              </button>

              {showTechnicalDocs && (
                <div className="px-6 pb-6 space-y-6 text-sm text-gray-700 border-t">

                  {/* 1. Core Framework */}
                  <div className="pt-4">
                    <h4 className="font-bold text-gray-800 mb-2">1. Core Framework: Leontief Input-Output Model</h4>
                    <p className="mb-2">
                      The model uses the standard open Leontief demand-driven framework. Given a technical coefficients
                      matrix <strong>A</strong> (14&times;14 sectors), the Leontief inverse is:
                    </p>
                    <div className="bg-gray-100 rounded p-3 font-mono text-center mb-2">
                      L = (I &minus; A)<sup>&minus;1</sup>
                    </div>
                    <p className="mb-2">
                      Employment effects of a demand shock vector <strong>&Delta;d</strong> are calculated as:
                    </p>
                    <div className="bg-gray-100 rounded p-3 font-mono text-center mb-2">
                      &Delta;employment = e &middot; L &middot; &Delta;d
                    </div>
                    <p>
                      where <strong>e</strong> is the vector of employment coefficients (jobs per million USD of output).
                    </p>
                  </div>

                  {/* 2. Sectors */}
                  <div>
                    <h4 className="font-bold text-gray-800 mb-2">2. Sectors (14)</h4>
                    <div className="grid grid-cols-2 gap-1 text-xs">
                      {['Agriculture', 'Mining', 'Manufacturing', 'Textiles & Apparel',
                        'Automotive', 'Food Processing', 'Chemicals', 'Construction',
                        'Utilities', 'Wholesale & Retail Trade', 'Transport & Logistics',
                        'Financial Services', 'Public Services', 'Other Services'].map(s => (
                        <span key={s} className="bg-gray-50 rounded px-2 py-1">{s}</span>
                      ))}
                    </div>
                  </div>

                  {/* 3. Employment Multipliers */}
                  <div>
                    <h4 className="font-bold text-gray-800 mb-2">3. Employment Multipliers</h4>
                    <p className="mb-2">Each sector has three multiplier components:</p>
                    <ul className="space-y-1 ml-4 list-disc">
                      <li><strong>Direct</strong>: Jobs created per $1M output in the sector itself</li>
                      <li><strong>Indirect</strong>: Jobs created in upstream supplier sectors via inter-industry linkages</li>
                      <li><strong>Induced</strong>: Jobs created through household consumption of wages earned</li>
                    </ul>
                    <p className="mt-2">
                      <strong>Type I multiplier</strong> = Direct + Indirect. <strong>Type II multiplier</strong> = Direct + Indirect + Induced.
                    </p>
                    <p className="mt-2">
                      <strong>Data sources</strong>: South Africa uses OECD TiVA/ICIO 2023 (reference year 2020) with Stats SA Labour Force Survey demographics.
                      Tunisia, Viet Nam, Thailand, and Mozambique use stylized estimates based on ILO statistics and regional patterns.
                    </p>
                  </div>

                  {/* 4. GDP and Sector Shares */}
                  <div>
                    <h4 className="font-bold text-gray-800 mb-2">4. Country GDP and Sector Shares</h4>
                    <table className="w-full text-xs border-collapse">
                      <thead>
                        <tr className="bg-gray-100">
                          <th className="p-2 text-left border">Country</th>
                          <th className="p-2 text-right border">GDP ($M)</th>
                          <th className="p-2 text-right border">Agriculture</th>
                          <th className="p-2 text-right border">Manufacturing</th>
                          <th className="p-2 text-right border">Services</th>
                        </tr>
                      </thead>
                      <tbody>
                        {[
                          ['South Africa', '400,000', '2.5%', '12.0%', '55.0%'],
                          ['Tunisia', '50,000', '10.0%', '15.0%', '50.0%'],
                          ['Viet Nam', '450,000', '12.0%', '16.0%', '34.0%'],
                          ['Thailand', '515,000', '8.0%', '18.0%', '40.0%'],
                          ['Mozambique', '22,750', '30.0%', '7.0%', '48.0%'],
                        ].map(([c, gdp, ag, mfg, svc]) => (
                          <tr key={c}>
                            <td className="p-2 border">{c}</td>
                            <td className="p-2 border text-right">{gdp}</td>
                            <td className="p-2 border text-right">{ag}</td>
                            <td className="p-2 border text-right">{mfg}</td>
                            <td className="p-2 border text-right">{svc}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    <p className="mt-1 text-xs text-gray-500">Sources: World Bank WDI 2024, national statistics offices. Approximate values.</p>
                  </div>

                  {/* 5. Policy Transmission */}
                  <div>
                    <h4 className="font-bold text-gray-800 mb-2">5. Policy Transmission: From Levers to Demand Shocks</h4>
                    <p className="mb-2">Each policy lever is translated into a sectoral demand shock (&Delta;d) in millions USD:</p>

                    <div className="space-y-3">
                      <div className="bg-blue-50 rounded p-3">
                        <h5 className="font-medium text-blue-800">a) Import Tariffs</h5>
                        <p className="mt-1">Tariff effects use a non-linear response curve:</p>
                        <ul className="mt-1 ml-4 list-disc text-xs">
                          <li>Positive effects peak at 8-12% tariff rate (domestic substitution)</li>
                          <li>Above ~20%, negative effects dominate (retaliation, inefficiency)</li>
                          <li>&Delta;d = sector_GDP &times; tariff_response(rate) &times; protection_effectiveness</li>
                          <li>Aggregate tariffs above 80% trigger a retaliation penalty (0.85&times; multiplier)</li>
                        </ul>
                      </div>

                      <div className="bg-green-50 rounded p-3">
                        <h5 className="font-medium text-green-800">b) Subsidies</h5>
                        <p className="mt-1">Direct demand stimulus with diminishing returns:</p>
                        <ul className="mt-1 ml-4 list-disc text-xs">
                          <li>&Delta;d = sector_GDP &times; (subsidy_rate / 100) &times; effectiveness</li>
                          <li>Effectiveness = 0.7 at &le;5%, declining to ~0.55 above 10%</li>
                          <li>Total subsidy commitment above 50% triggers fiscal crowding-out (0.8&times;)</li>
                        </ul>
                      </div>

                      <div className="bg-orange-50 rounded p-3">
                        <h5 className="font-medium text-orange-800">c) SME Stimulus</h5>
                        <p className="mt-1">Broad-based stimulus with fiscal multiplier:</p>
                        <ul className="mt-1 ml-4 list-disc text-xs">
                          <li>&Delta;d = GDP &times; (sme_pct / 100) &times; fiscal_multiplier &times; sector_weight</li>
                          <li>Fiscal multiplier: 1.0 at 1% GDP, declining to ~0.75 at 3%+ (IMF/World Bank empirical range for developing countries)</li>
                          <li>Distributed across labour-intensive sectors (trade, services, food processing, textiles, construction)</li>
                        </ul>
                      </div>

                      <div className="bg-purple-50 rounded p-3">
                        <h5 className="font-medium text-purple-800">d) Industrial Policy &amp; Productivity Investment</h5>
                        <p className="mt-1">Investment as % of sector GDP in manufacturing sectors:</p>
                        <ul className="mt-1 ml-4 list-disc text-xs">
                          <li>&Delta;d = sector_GDP &times; (prod_pct / 100) &times; effectiveness &times; time_multiplier</li>
                          <li>Targets 4 sectors: manufacturing, automotive, chemicals, food processing</li>
                          <li>Effectiveness = 0.5 at &le;5%, diminishing above (0.5 &minus; (pct &minus; 5) &times; 0.03)</li>
                          <li>Time-dependent multiplier: &minus;0.15&times; at 1 year (displacement), +0.45&times; at 3 years (competitiveness), +1.0&times; at 5 years (expanded markets) — Acemoglu &amp; Restrepo (2018)</li>
                          <li>Job quality bonus at longer horizons: +10% (3yr), +20% (5yr)</li>
                          <li>Fiscal cost: government co-finances 30% of investment</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* 6. Policy Synergies */}
                  <div>
                    <h4 className="font-bold text-gray-800 mb-2">6. Policy Synergy Multiplier</h4>
                    <p>
                      A balanced policy mix (2-3 instruments) receives a modest synergy bonus (1.05&times; for 2 policies, 1.08&times; for 3).
                      Complementary combinations (e.g., subsidies + productivity investment, SME + moderate tariffs) receive an additional +5%.
                      Non-complementary combinations incur a &minus;10% penalty. When average tariff and average subsidy both exceed 8%, a rent-seeking penalty replaces the synergy bonus.
                    </p>
                  </div>

                  {/* 7. Time Scaling */}
                  <div>
                    <h4 className="font-bold text-gray-800 mb-2">7. Time Horizon Scaling</h4>
                    <table className="w-full text-xs border-collapse">
                      <thead>
                        <tr className="bg-gray-100">
                          <th className="p-2 text-left border">Horizon</th>
                          <th className="p-2 text-right border">Direct</th>
                          <th className="p-2 text-right border">Indirect</th>
                          <th className="p-2 text-right border">Induced</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr><td className="p-2 border">Short (1 year)</td><td className="p-2 border text-right">0.6&times;</td><td className="p-2 border text-right">0.3&times;</td><td className="p-2 border text-right">0.2&times;</td></tr>
                        <tr><td className="p-2 border">Medium (3 years)</td><td className="p-2 border text-right">1.0&times;</td><td className="p-2 border text-right">0.8&times;</td><td className="p-2 border text-right">0.6&times;</td></tr>
                        <tr><td className="p-2 border">Long (5 years)</td><td className="p-2 border text-right">1.0&times;</td><td className="p-2 border text-right">1.0&times;</td><td className="p-2 border text-right">1.0&times;</td></tr>
                      </tbody>
                    </table>
                    <p className="mt-1 text-xs text-gray-500">Direct effects materialise faster than indirect/induced effects.</p>
                  </div>

                  {/* 8. Demographic Disaggregation */}
                  <div>
                    <h4 className="font-bold text-gray-800 mb-2">8. Demographic Disaggregation</h4>
                    <p>Each sector carries demographic shares from TiVA/ILO data:</p>
                    <ul className="mt-1 ml-4 list-disc">
                      <li><strong>Female share</strong>: Proportion of sector workforce that is female</li>
                      <li><strong>Youth share</strong>: Proportion aged 15-24</li>
                      <li><strong>Informal share</strong>: Proportion in informal employment</li>
                    </ul>
                    <p className="mt-1">
                      Aggregate shares are weighted averages across sectors, weighted by jobs created per sector.
                    </p>
                  </div>

                  {/* 9. Job Quality Metrics */}
                  <div>
                    <h4 className="font-bold text-gray-800 mb-2">9. Job Quality Metrics</h4>
                    <p className="mb-2">Three quality indicators are calculated from sector-level data:</p>

                    <div className="space-y-2">
                      <div>
                        <h5 className="font-medium">a) Formalization Rate</h5>
                        <p className="text-xs">&nbsp;&nbsp;= (1 &minus; weighted_informal_share) &times; 100%. Uses informal_share from employment multiplier data per sector.</p>
                      </div>
                      <div>
                        <h5 className="font-medium">b) Working Poverty Risk</h5>
                        <p className="text-xs">&nbsp;&nbsp;= weighted average of sector-specific poverty risk rates. Based on ILO estimates:
                          agriculture 85%, trade 70%, other services 65%, construction 55%, transport 50%,
                          textiles 45%, food processing 40%, manufacturing 30%, public services 25%,
                          chemicals 25%, automotive 20%, mining 15%, utilities 15%, finance 10%.</p>
                      </div>
                      <div>
                        <h5 className="font-medium">c) Average Productivity</h5>
                        <p className="text-xs">&nbsp;&nbsp;= weighted average of sector GDP per worker (USD/year).
                          Ranges from $3,500 (agriculture) to $28,000 (finance).
                          Categorised as LOW (&lt;$8K), MEDIUM ($8-15K), HIGH (&gt;$15K).</p>
                      </div>
                    </div>
                  </div>

                  {/* 10. Cost-Benefit Analysis */}
                  <div>
                    <h4 className="font-bold text-gray-800 mb-2">10. Cost-Benefit Analysis</h4>
                    <p className="mb-2">All costs are calculated as annual flows:</p>
                    <ul className="ml-4 list-disc space-y-1">
                      <li><strong>Tariff revenue (net)</strong> = remaining_imports &times; tariff_rate, after behavioral import reduction using sector-specific elasticities (Kee, Nicita &amp; Olarreaga 2008; range &minus;0.3 to &minus;2.0)</li>
                      <li><strong>Tariff downstream cost</strong> = linkage_coefficient &times; tariff_rate &times; downstream_sector_GDP &times; 0.4 pass-through; applied to all downstream sectors with linkage &gt;0.07</li>
                      <li><strong>Deadweight loss</strong> = 0.5 &times; tariff_rate&sup2; &times; |elasticity| &times; import_value (Harberger triangle)</li>
                      <li><strong>Subsidy cost</strong> = subsidy_rate &times; sector_GDP</li>
                      <li><strong>SME stimulus cost</strong> = sme_pct &times; GDP (less 20% tax recapture)</li>
                      <li><strong>Productivity cost</strong> = prod_pct &times; sector_GDP &times; 0.30 (30% government co-financing)</li>
                      <li><strong>Cost per job (fiscal)</strong> = net_fiscal_impact / total_jobs</li>
                      <li><strong>Cost per job (economic)</strong> = total_economic_cost / total_jobs (includes deadweight loss)</li>
                    </ul>
                  </div>

                  {/* 11. Technical Coefficients */}
                  <div>
                    <h4 className="font-bold text-gray-800 mb-2">11. Technical Coefficients Matrix (A)</h4>
                    <p>
                      The inter-industry linkage matrix is stylized for each country, reflecting key supply chain relationships:
                    </p>
                    <ul className="mt-1 ml-4 list-disc text-xs">
                      <li>Agriculture &rarr; Food Processing (strong linkage, 0.18-0.26)</li>
                      <li>Mining &rarr; Manufacturing (raw material inputs, 0.10-0.15)</li>
                      <li>Manufacturing &rarr; Automotive (component supply, 0.18-0.28)</li>
                      <li>Chemicals &rarr; Textiles (input materials, 0.08-0.12)</li>
                      <li>Background coefficients: random uniform 0.01-0.05, seeded with np.random.seed(42) for reproducibility</li>
                      <li>Row sums capped at 0.9 to ensure matrix invertibility</li>
                    </ul>
                    <p className="mt-1 text-xs text-gray-500">
                      These are NOT derived from national supply-use tables. Country-specific patterns reflect known
                      structural features (e.g., Thailand's automotive supply chain, Mozambique's agriculture dominance).
                    </p>
                  </div>

                  {/* 12. Confidence Intervals */}
                  <div>
                    <h4 className="font-bold text-gray-800 mb-2">12. Uncertainty and Confidence Intervals</h4>
                    <p>
                      Confidence intervals are data-quality-aware. OECD-backed countries (ZAF, VNM, THA): &plusmn;10% for most sectors, &plusmn;15% for agriculture and informal sectors. Stylized countries (TUN, MOZ): &plusmn;25% for most sectors, &plusmn;30% for agriculture and informal sectors. The data quality level is indicated by the badge shown in the results header.
                    </p>
                  </div>

                  <div className="pt-4 border-t text-xs text-gray-500">
                    <p>Last updated: March 2026 (v0.8.0). This documentation is maintained alongside the codebase and updated with each model change.</p>
                  </div>
                </div>
              )}
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
