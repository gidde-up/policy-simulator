import React, { useState } from 'react';
import { TrendingUp, TrendingDown, Users, Briefcase, AlertCircle, HelpCircle, ArrowRight, ArrowDown, ArrowUp, Database, CheckCircle, DollarSign, Scale, Award, Activity, Shield, Sparkles } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend, ComposedChart, Line } from 'recharts';

// Helper component for before/after unemployment display
function UnemploymentIndicator({ label, icon, current, projected, change, color }) {
  const isImprovement = change < 0; // Negative change in unemployment is good
  const changeAbs = Math.abs(change);

  const colorClasses = {
    gray: { bg: 'bg-gray-100', text: 'text-gray-700', accent: 'bg-gray-500' },
    amber: { bg: 'bg-amber-50', text: 'text-amber-700', accent: 'bg-amber-500' },
    pink: { bg: 'bg-pink-50', text: 'text-pink-700', accent: 'bg-pink-500' },
    blue: { bg: 'bg-blue-50', text: 'text-blue-700', accent: 'bg-blue-500' },
  };

  const colors = colorClasses[color] || colorClasses.gray;

  return (
    <div className={`${colors.bg} rounded-lg p-4`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className={colors.text}>{icon}</span>
          <span className={`font-medium ${colors.text}`}>{label}</span>
        </div>
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          isImprovement ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}>
          {isImprovement ? 'Improving' : 'Worsening'}
        </span>
      </div>

      <div className="flex items-center justify-between">
        {/* Before */}
        <div className="text-center flex-1">
          <div className="text-xs text-gray-500 mb-1">Current</div>
          <div className="text-2xl font-bold text-gray-800">{current.toFixed(1)}%</div>
        </div>

        {/* Arrow */}
        <div className="flex flex-col items-center px-4">
          <ArrowRight className={`w-6 h-6 ${isImprovement ? 'text-green-500' : 'text-red-500'}`} />
          <span className={`text-xs font-medium mt-1 ${isImprovement ? 'text-green-600' : 'text-red-600'}`}>
            {isImprovement ? '-' : '+'}{changeAbs.toFixed(2)}pp
          </span>
        </div>

        {/* After */}
        <div className="text-center flex-1">
          <div className="text-xs text-gray-500 mb-1">Projected</div>
          <div className={`text-2xl font-bold ${isImprovement ? 'text-green-600' : 'text-red-600'}`}>
            {projected.toFixed(1)}%
          </div>
        </div>

        {/* Visual bar comparison */}
        <div className="flex-1 ml-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-400 w-10">Before</span>
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gray-500 h-2 rounded-full transition-all"
                  style={{ width: `${Math.min(100, current * 2)}%` }}
                />
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-400 w-10">After</span>
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${isImprovement ? 'bg-green-500' : 'bg-red-500'}`}
                  style={{ width: `${Math.min(100, projected * 2)}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ResultsPanel({ results, loading, interpretation }) {
  const [warningDismissed, setWarningDismissed] = useState(false);

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-md p-8">
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-500">Running simulation...</p>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="bg-white rounded-xl shadow-md p-8">
        <div className="flex flex-col items-center justify-center space-y-4 text-gray-400">
          <HelpCircle className="w-16 h-16" />
          <p className="text-lg font-medium">No simulation results yet</p>
          <p className="text-sm text-center">
            Adjust the policy parameters on the left and click "Run Simulation" to see the projected employment effects.
          </p>
        </div>
      </div>
    );
  }

  const { aggregate, sector_effects } = results;
  const totalJobs = aggregate.total_jobs;
  const isPositive = totalJobs > 0;

  // Prepare sector chart data
  const sectorData = sector_effects
    .filter(s => Math.abs(s.employment_effect.total_jobs) > 1)
    .map(s => ({
      name: s.sector.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
      jobs: Math.round(s.employment_effect.total_jobs),
      direct: Math.round(s.employment_effect.direct_jobs),
      indirect: Math.round(s.employment_effect.indirect_jobs),
    }))
    .sort((a, b) => b.jobs - a.jobs);

  // Demographic pie chart data
  const genderData = [
    { name: 'Female', value: aggregate.female_share * 100, color: '#EC4899' },
    { name: 'Male', value: aggregate.male_share * 100, color: '#3B82F6' },
  ];

  const ageData = [
    { name: 'Youth (15-24)', value: aggregate.youth_share * 100, color: '#F59E0B' },
    { name: 'Adults (25+)', value: aggregate.adult_share * 100, color: '#6366F1' },
  ];

  const jobQualityData = [
    { name: 'Formal', value: aggregate.formal_share * 100, color: '#10B981' },
    { name: 'Informal', value: aggregate.informal_share * 100, color: '#EF4444' },
  ];

  const dataQuality = results.data_source?.quality;
  const isResearchGrade = dataQuality === 'research-grade';

  return (
    <div className="space-y-4">
      {/* Model Boundaries Warning — dismissible, not skippable on first view */}
      {!warningDismissed && (
        <div className="bg-amber-50 border border-amber-300 rounded-xl p-4">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-semibold text-amber-800 text-sm">Model boundaries — read before interpreting results</p>
                <p className="text-amber-700 text-xs mt-1">
                  This is a <strong>partial equilibrium, fixed-price Input-Output model</strong>. Results are illustrative, not forecasts.
                  The model does <strong>not</strong> capture: wage pressure from labour market tightening; crowding-out of private investment;
                  exchange rate effects of tariffs; price level changes; or net economy-wide employment displacement
                  (figures shown are <strong>gross</strong> job effects, not net of sector reallocation).
                </p>
              </div>
            </div>
            <button
              onClick={() => setWarningDismissed(true)}
              className="ml-3 text-amber-500 hover:text-amber-700 text-xs underline flex-shrink-0"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Data Quality Badge */}
      {dataQuality && (
        <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-medium w-fit ${
          isResearchGrade
            ? 'bg-green-50 border border-green-200 text-green-700'
            : 'bg-yellow-50 border border-yellow-200 text-yellow-700'
        }`}>
          <Database className="w-3 h-3" />
          <span>
            {isResearchGrade ? 'OECD TiVA data — research-grade' : 'Stylized estimates — illustrative only'}
          </span>
          {results.data_source?.reference_year && (
            <span className="text-gray-400">({results.data_source.reference_year})</span>
          )}
        </div>
      )}

      {/* AI Interpretation */}
      {interpretation && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-start space-x-3">
          <Sparkles className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm font-semibold text-blue-800 mb-1">AI Interpretation</p>
            <p className="text-sm text-blue-700 whitespace-pre-line">{interpretation}</p>
          </div>
        </div>
      )}

      {/* Main Results Card */}
      <div className={`rounded-xl shadow-md p-6 ${isPositive ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-800">Employment Impact</h2>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${isPositive ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}`}>
            {results.time_horizon} Year Projection
          </span>
        </div>

        <div className="flex items-center space-x-4">
          <div className={`p-4 rounded-xl ${isPositive ? 'bg-green-100' : 'bg-red-100'}`}>
            {isPositive ? (
              <TrendingUp className="w-10 h-10 text-green-600" />
            ) : (
              <TrendingDown className="w-10 h-10 text-red-600" />
            )}
          </div>
          <div>
            <div className={`text-4xl font-bold ${isPositive ? 'text-green-700' : 'text-red-700'}`}>
              {isPositive ? '+' : ''}{Math.round(totalJobs).toLocaleString()}
              {results.baseline_indicators?.labor_force?.current_value > 0 && (
                <span className="text-lg ml-2 font-semibold opacity-75">
                  ({isPositive ? '+' : ''}{(totalJobs / results.baseline_indicators.labor_force.current_value * 100).toFixed(2)}%)
                </span>
              )}
            </div>
            <div className="text-gray-600">
              Total Jobs {isPositive ? 'Created' : 'Lost'}
              {results.baseline_indicators?.labor_force?.current_value > 0 && (
                <span className="text-gray-400 ml-1">(% of labour force)</span>
              )}
            </div>
            <div className="text-xs text-gray-400 mt-1">
              Gross figure — does not account for jobs displaced in unprotected sectors
            </div>
          </div>
        </div>

        {/* Confidence interval */}
        <div className="mt-4 flex items-center text-sm text-gray-500">
          <AlertCircle className="w-4 h-4 mr-2" />
          <span>
            Estimated range: {Math.round(aggregate.confidence_low).toLocaleString()} to {Math.round(aggregate.confidence_high).toLocaleString()} jobs
          </span>
        </div>
      </div>

      {/* Job Breakdown */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="font-bold text-gray-800 mb-4">Job Effect Breakdown</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-700">
              {Math.round(aggregate.direct_jobs).toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Direct Jobs</div>
            <div className="text-xs text-gray-400 mt-1">In targeted sectors</div>
          </div>
          <div className="text-center p-3 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-700">
              {Math.round(aggregate.indirect_jobs).toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Indirect Jobs</div>
            <div className="text-xs text-gray-400 mt-1">Supply chain effects</div>
          </div>
          <div className="text-center p-3 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-700">
              {Math.round(aggregate.induced_jobs).toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Induced Jobs</div>
            <div className="text-xs text-gray-400 mt-1">Spending effects</div>
          </div>
        </div>
      </div>

      {/* Job Quality Analysis */}
      {results.job_quality && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="font-bold text-gray-800 mb-2 flex items-center">
            <Award className="w-5 h-5 mr-2 text-blue-600" />
            Job Quality Analysis
          </h3>
          <p className="text-sm text-gray-500 mb-4">
            Quality indicators for jobs created: formality, productivity, and working poverty risk
          </p>

          <div className="grid grid-cols-3 gap-4 mb-6">
            {/* Formalization Rate */}
            <div className={`p-4 rounded-lg border-2 ${
              results.job_quality.formalization_rate >= 60 ? 'bg-green-50 border-green-200' :
              results.job_quality.formalization_rate >= 40 ? 'bg-amber-50 border-amber-200' :
              'bg-red-50 border-red-200'
            }`}>
              <div className="flex items-center space-x-2 mb-2">
                <Shield className={`w-5 h-5 ${
                  results.job_quality.formalization_rate >= 60 ? 'text-green-600' :
                  results.job_quality.formalization_rate >= 40 ? 'text-amber-600' :
                  'text-red-600'
                }`} />
                <span className="text-xs font-medium text-gray-600">Formalization</span>
              </div>
              <div className={`text-3xl font-bold ${
                results.job_quality.formalization_rate >= 60 ? 'text-green-700' :
                results.job_quality.formalization_rate >= 40 ? 'text-amber-700' :
                'text-red-700'
              }`}>
                {results.job_quality.formalization_rate.toFixed(0)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {Math.round(results.job_quality.formal_jobs).toLocaleString()} formal jobs
              </div>
              <div className="text-xs text-gray-400">
                {Math.round(results.job_quality.informal_jobs).toLocaleString()} informal jobs
              </div>
            </div>

            {/* Working Poverty Risk */}
            <div className={`p-4 rounded-lg border-2 ${
              results.job_quality.working_poverty_risk <= 30 ? 'bg-green-50 border-green-200' :
              results.job_quality.working_poverty_risk <= 60 ? 'bg-amber-50 border-amber-200' :
              'bg-red-50 border-red-200'
            }`}>
              <div className="flex items-center space-x-2 mb-2">
                <AlertCircle className={`w-5 h-5 ${
                  results.job_quality.working_poverty_risk <= 30 ? 'text-green-600' :
                  results.job_quality.working_poverty_risk <= 60 ? 'text-amber-600' :
                  'text-red-600'
                }`} />
                <span className="text-xs font-medium text-gray-600">Working Poverty Risk</span>
              </div>
              <div className={`text-3xl font-bold ${
                results.job_quality.working_poverty_risk <= 30 ? 'text-green-700' :
                results.job_quality.working_poverty_risk <= 60 ? 'text-amber-700' :
                'text-red-700'
              }`}>
                {results.job_quality.working_poverty_risk.toFixed(0)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {Math.round(results.job_quality.jobs_above_poverty_line).toLocaleString()} above poverty line
              </div>
              <div className="text-xs text-gray-400">
                {Math.round(results.job_quality.jobs_below_poverty_line).toLocaleString()} at poverty risk
              </div>
            </div>

            {/* Productivity Level */}
            <div className={`p-4 rounded-lg border-2 ${
              results.job_quality.productivity_category === 'high' ? 'bg-green-50 border-green-200' :
              results.job_quality.productivity_category === 'medium' ? 'bg-amber-50 border-amber-200' :
              'bg-red-50 border-red-200'
            }`}>
              <div className="flex items-center space-x-2 mb-2">
                <Activity className={`w-5 h-5 ${
                  results.job_quality.productivity_category === 'high' ? 'text-green-600' :
                  results.job_quality.productivity_category === 'medium' ? 'text-amber-600' :
                  'text-red-600'
                }`} />
                <span className="text-xs font-medium text-gray-600">Avg Productivity</span>
              </div>
              <div className={`text-2xl font-bold ${
                results.job_quality.productivity_category === 'high' ? 'text-green-700' :
                results.job_quality.productivity_category === 'medium' ? 'text-amber-700' :
                'text-red-700'
              }`}>
                ${(results.job_quality.avg_productivity_usd / 1000).toFixed(1)}K
              </div>
              <div className="text-xs text-gray-500 mt-1">
                per worker/year
              </div>
              <div className={`text-xs font-medium mt-1 ${
                results.job_quality.productivity_category === 'high' ? 'text-green-600' :
                results.job_quality.productivity_category === 'medium' ? 'text-amber-600' :
                'text-red-600'
              }`}>
                {results.job_quality.productivity_category.toUpperCase()} productivity
              </div>
            </div>
          </div>

          {/* Sector Composition Bar */}
          <div className="mt-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Jobs by Broad Sector</h4>
            <div className="flex h-8 rounded-lg overflow-hidden border border-gray-200">
              {results.job_quality.agriculture_jobs > 0 && (
                <div
                  className="bg-amber-500 flex items-center justify-center text-xs text-white font-medium"
                  style={{ width: `${(results.job_quality.agriculture_jobs / aggregate.total_jobs * 100).toFixed(1)}%` }}
                  title={`Agriculture: ${Math.round(results.job_quality.agriculture_jobs).toLocaleString()} jobs`}
                >
                  {((results.job_quality.agriculture_jobs / aggregate.total_jobs * 100) > 10) &&
                    `Agri ${(results.job_quality.agriculture_jobs / aggregate.total_jobs * 100).toFixed(0)}%`}
                </div>
              )}
              {results.job_quality.manufacturing_jobs > 0 && (
                <div
                  className="bg-blue-500 flex items-center justify-center text-xs text-white font-medium"
                  style={{ width: `${(results.job_quality.manufacturing_jobs / aggregate.total_jobs * 100).toFixed(1)}%` }}
                  title={`Manufacturing/Industry: ${Math.round(results.job_quality.manufacturing_jobs).toLocaleString()} jobs`}
                >
                  {((results.job_quality.manufacturing_jobs / aggregate.total_jobs * 100) > 10) &&
                    `Mfg ${(results.job_quality.manufacturing_jobs / aggregate.total_jobs * 100).toFixed(0)}%`}
                </div>
              )}
              {results.job_quality.services_jobs > 0 && (
                <div
                  className="bg-purple-500 flex items-center justify-center text-xs text-white font-medium"
                  style={{ width: `${(results.job_quality.services_jobs / aggregate.total_jobs * 100).toFixed(1)}%` }}
                  title={`Services: ${Math.round(results.job_quality.services_jobs).toLocaleString()} jobs`}
                >
                  {((results.job_quality.services_jobs / aggregate.total_jobs * 100) > 10) &&
                    `Svc ${(results.job_quality.services_jobs / aggregate.total_jobs * 100).toFixed(0)}%`}
                </div>
              )}
            </div>
            <div className="flex justify-between mt-2 text-xs text-gray-600">
              <span className="flex items-center">
                <span className="w-3 h-3 rounded bg-amber-500 mr-1"></span>
                Agriculture: {Math.round(results.job_quality.agriculture_jobs).toLocaleString()}
              </span>
              <span className="flex items-center">
                <span className="w-3 h-3 rounded bg-blue-500 mr-1"></span>
                Manufacturing: {Math.round(results.job_quality.manufacturing_jobs).toLocaleString()}
              </span>
              <span className="flex items-center">
                <span className="w-3 h-3 rounded bg-purple-500 mr-1"></span>
                Services: {Math.round(results.job_quality.services_jobs).toLocaleString()}
              </span>
            </div>
          </div>

          {/* Interpretation Note */}
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-xs text-blue-800">
            <strong>Interpreting Job Quality:</strong> High formalization rates, low working poverty risk, and high productivity indicate
            better quality jobs with higher wages and social protection. Agriculture-heavy scenarios often create many informal,
            low-productivity jobs with high poverty risk, while manufacturing/services create fewer but higher-quality jobs.
          </div>
        </div>
      )}

      {/* Cost Analysis */}
      {results.costs && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="font-bold text-gray-800 mb-4 flex items-center">
            <Scale className="w-5 h-5 mr-2 text-gray-600" />
            Cost-Benefit Analysis
            <span className="ml-2 text-xs font-normal text-gray-500">(annual figures)</span>
          </h3>

          {/* Cost per Job - Key Metric */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className={`p-4 rounded-lg ${
              results.costs.cost_per_job_fiscal !== null && results.costs.cost_per_job_fiscal < 0
                ? 'bg-green-50 border border-green-200'
                : 'bg-amber-50 border border-amber-200'
            }`}>
              <div className="flex items-center space-x-2 mb-2">
                <DollarSign className="w-5 h-5 text-gray-600" />
                <span className="font-medium text-gray-700">Fiscal Cost per Job/Year</span>
              </div>
              {results.costs.cost_per_job_fiscal !== null ? (
                <>
                  <div className={`text-2xl font-bold ${
                    results.costs.cost_per_job_fiscal < 0 ? 'text-green-700' : 'text-amber-700'
                  }`}>
                    {results.costs.cost_per_job_fiscal < 0 ? '-$' : '$'}
                    {Math.abs(results.costs.cost_per_job_fiscal) >= 1000
                      ? `${(Math.abs(results.costs.cost_per_job_fiscal) / 1000).toFixed(1)}K`
                      : Math.abs(results.costs.cost_per_job_fiscal).toFixed(0)}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {results.costs.cost_per_job_fiscal < 0
                      ? 'Annual net revenue per job'
                      : 'Annual government spending per job'}
                  </div>
                </>
              ) : (
                <div className="text-lg text-gray-500">N/A (net job loss)</div>
              )}
            </div>

            <div className="p-4 rounded-lg bg-red-50 border border-red-200">
              <div className="flex items-center space-x-2 mb-2">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <span className="font-medium text-gray-700">Economic Cost per Job/Year</span>
              </div>
              {results.costs.cost_per_job_economic !== null ? (
                <>
                  <div className="text-2xl font-bold text-red-700">
                    ${results.costs.cost_per_job_economic >= 1000
                      ? `${(results.costs.cost_per_job_economic / 1000).toFixed(1)}K`
                      : results.costs.cost_per_job_economic.toFixed(0)}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Annual cost incl. deadweight loss
                  </div>
                </>
              ) : (
                <div className="text-lg text-gray-500">N/A (net job loss)</div>
              )}
            </div>
          </div>

          {/* Fiscal Breakdown */}
          <div className="space-y-3">
            <h4 className="font-medium text-gray-700 text-sm">Annual Fiscal Impact Breakdown</h4>
            <div className="grid grid-cols-2 gap-3 text-sm">
              {/* Tariff Revenue */}
              {results.costs.tariff_revenue_net > 0 && (
                <div className="flex justify-between items-center p-2 bg-green-50 rounded">
                  <span className="text-gray-600">Tariff Revenue (net)</span>
                  <span className="font-medium text-green-700">
                    +${(results.costs.tariff_revenue_net / 1000).toFixed(1)}B
                  </span>
                </div>
              )}

              {/* Tariff Trade Reduction */}
              {results.costs.tariff_trade_reduction > 0 && (
                <div className="flex justify-between items-center p-2 bg-amber-50 rounded">
                  <span className="text-gray-600">Import Reduction</span>
                  <span className="font-medium text-amber-700">
                    -${(results.costs.tariff_trade_reduction / 1000).toFixed(1)}B
                  </span>
                </div>
              )}

              {/* Deadweight Loss */}
              {results.costs.tariff_deadweight_loss > 0 && (
                <div className="flex justify-between items-center p-2 bg-red-50 rounded">
                  <span className="text-gray-600">Efficiency Loss (DWL)</span>
                  <span className="font-medium text-red-700">
                    -${(results.costs.tariff_deadweight_loss / 1000).toFixed(1)}B
                  </span>
                </div>
              )}

              {/* Subsidy Cost */}
              {results.costs.subsidy_cost > 0 && (
                <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                  <span className="text-gray-600">Subsidy Spending</span>
                  <span className="font-medium text-gray-700">
                    -${(results.costs.subsidy_cost / 1000).toFixed(1)}B
                  </span>
                </div>
              )}

              {/* SME Stimulus */}
              {results.costs.sme_stimulus_cost > 0 && (
                <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                  <span className="text-gray-600">SME Stimulus</span>
                  <span className="font-medium text-gray-700">
                    -${(results.costs.sme_stimulus_cost / 1000).toFixed(1)}B
                  </span>
                </div>
              )}

              {/* Productivity Investment */}
              {results.costs.productivity_cost > 0 && (
                <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                  <span className="text-gray-600">Productivity Investment</span>
                  <span className="font-medium text-gray-700">
                    -${(results.costs.productivity_cost / 1000).toFixed(1)}B
                  </span>
                </div>
              )}
            </div>

            {/* Net Fiscal Impact */}
            <div className={`flex justify-between items-center p-3 rounded-lg mt-3 ${
              results.costs.net_fiscal_impact >= 0
                ? 'bg-green-100 border border-green-300'
                : 'bg-red-100 border border-red-300'
            }`}>
              <div>
                <span className="font-medium text-gray-700">Net Annual Fiscal Impact</span>
                {results.baseline_indicators?.gov_expenditure_usd > 0 && (
                  <span className="text-xs text-gray-400 ml-1">(% of public expenditure)</span>
                )}
              </div>
              <div className="text-right">
                <span className={`font-bold text-lg ${
                  results.costs.net_fiscal_impact >= 0 ? 'text-green-700' : 'text-red-700'
                }`}>
                  {results.costs.net_fiscal_impact >= 0 ? '+' : ''}
                  ${(results.costs.net_fiscal_impact / 1000).toFixed(2)}B
                  {results.baseline_indicators?.gov_expenditure_usd > 0 && (
                    <span className="text-sm ml-1 font-semibold opacity-75">
                      ({results.costs.net_fiscal_impact >= 0 ? '+' : ''}
                      {(results.costs.net_fiscal_impact / results.baseline_indicators.gov_expenditure_usd * 100).toFixed(2)}%)
                    </span>
                  )}
                </span>
              </div>
            </div>

            {/* Warning about tariff revenue illusion */}
            {results.costs.tariff_revenue_net > 0 && results.costs.tariff_deadweight_loss > 0 && (
              <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800">
                <strong>Note:</strong> While tariffs generate fiscal revenue, they also create economic costs
                (deadweight loss, reduced trade, higher prices) that may exceed the revenue benefit.
                The economic cost per job accounts for these hidden costs.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Enhanced Sector Chart with Direct/Indirect Breakdown */}
      {sectorData.length > 0 && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="font-bold text-gray-800 mb-2">Sectoral Employment Impact</h3>
          <p className="text-sm text-gray-500 mb-4">Jobs created/lost by sector (showing direct and indirect effects)</p>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sectorData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(value, name) => [
                    value.toLocaleString(),
                    name === 'direct' ? 'Direct Jobs' : name === 'indirect' ? 'Indirect Jobs' : 'Total Jobs'
                  ]}
                  contentStyle={{ borderRadius: '8px' }}
                />
                <Legend />
                <Bar dataKey="direct" name="Direct Jobs" stackId="a" fill="#3B82F6" radius={[0, 0, 0, 0]} />
                <Bar dataKey="indirect" name="Indirect Jobs" stackId="a" fill="#8B5CF6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div className="flex items-center justify-center space-x-2 text-sm">
              <span className="w-4 h-4 rounded bg-blue-500" />
              <span className="text-gray-600">Direct: Jobs in targeted sectors</span>
            </div>
            <div className="flex items-center justify-center space-x-2 text-sm">
              <span className="w-4 h-4 rounded bg-purple-500" />
              <span className="text-gray-600">Indirect: Supply chain spillovers</span>
            </div>
          </div>
        </div>
      )}

      {/* Before/After Unemployment Indicators */}
      {results.baseline_indicators && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="font-bold text-gray-800 mb-2">Impact on Unemployment Rates</h3>
          <p className="text-sm text-gray-500 mb-4">Projected changes in key labor market indicators</p>
          <div className="space-y-4">
            {/* Total Unemployment */}
            {results.baseline_indicators.unemployment_total && (
              <UnemploymentIndicator
                label="Total Unemployment"
                icon={<Users className="w-5 h-5" />}
                current={results.baseline_indicators.unemployment_total.current_value}
                projected={results.baseline_indicators.unemployment_total.projected_value}
                change={results.baseline_indicators.unemployment_total.change}
                color="gray"
              />
            )}

            {/* Youth Unemployment */}
            {results.baseline_indicators.unemployment_youth && (
              <UnemploymentIndicator
                label="Youth Unemployment (15-24)"
                icon={<Users className="w-5 h-5" />}
                current={results.baseline_indicators.unemployment_youth.current_value}
                projected={results.baseline_indicators.unemployment_youth.projected_value}
                change={results.baseline_indicators.unemployment_youth.change}
                color="amber"
              />
            )}

            {/* Female Unemployment */}
            {results.baseline_indicators.unemployment_female && (
              <UnemploymentIndicator
                label="Female Unemployment"
                icon={<Users className="w-5 h-5" />}
                current={results.baseline_indicators.unemployment_female.current_value}
                projected={results.baseline_indicators.unemployment_female.projected_value}
                change={results.baseline_indicators.unemployment_female.change}
                color="pink"
              />
            )}

            {/* Male Unemployment */}
            {results.baseline_indicators.unemployment_male && (
              <UnemploymentIndicator
                label="Male Unemployment"
                icon={<Users className="w-5 h-5" />}
                current={results.baseline_indicators.unemployment_male.current_value}
                projected={results.baseline_indicators.unemployment_male.projected_value}
                change={results.baseline_indicators.unemployment_male.change}
                color="blue"
              />
            )}
          </div>
        </div>
      )}

      {/* Demographic Breakdown */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="font-bold text-gray-800 mb-4">Who Benefits?</h3>
        <div className="grid grid-cols-3 gap-4">
          {/* Gender */}
          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-2 text-center">By Gender</h4>
            <div className="h-32">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={genderData}
                    cx="50%"
                    cy="50%"
                    innerRadius={25}
                    outerRadius={45}
                    dataKey="value"
                  >
                    {genderData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value.toFixed(1)}%`]} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center space-x-4 text-xs">
              <span className="flex items-center">
                <span className="w-3 h-3 rounded-full bg-pink-500 mr-1" />
                Female {genderData[0].value.toFixed(0)}%
              </span>
              <span className="flex items-center">
                <span className="w-3 h-3 rounded-full bg-blue-500 mr-1" />
                Male {genderData[1].value.toFixed(0)}%
              </span>
            </div>
          </div>

          {/* Age */}
          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-2 text-center">By Age</h4>
            <div className="h-32">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={ageData}
                    cx="50%"
                    cy="50%"
                    innerRadius={25}
                    outerRadius={45}
                    dataKey="value"
                  >
                    {ageData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value.toFixed(1)}%`]} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center space-x-4 text-xs">
              <span className="flex items-center">
                <span className="w-3 h-3 rounded-full bg-amber-500 mr-1" />
                Youth {ageData[0].value.toFixed(0)}%
              </span>
              <span className="flex items-center">
                <span className="w-3 h-3 rounded-full bg-indigo-500 mr-1" />
                Adult {ageData[1].value.toFixed(0)}%
              </span>
            </div>
          </div>

          {/* Job Quality */}
          <div>
            <h4 className="text-sm font-medium text-gray-600 mb-2 text-center">Job Quality</h4>
            <div className="h-32">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={jobQualityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={25}
                    outerRadius={45}
                    dataKey="value"
                  >
                    {jobQualityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value.toFixed(1)}%`]} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center space-x-4 text-xs">
              <span className="flex items-center">
                <span className="w-3 h-3 rounded-full bg-green-500 mr-1" />
                Formal {jobQualityData[0].value.toFixed(0)}%
              </span>
              <span className="flex items-center">
                <span className="w-3 h-3 rounded-full bg-red-500 mr-1" />
                Informal {jobQualityData[1].value.toFixed(0)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Wage Effect */}
      {aggregate.avg_wage_effect !== 0 && (
        <div className="bg-white rounded-xl shadow-md p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Briefcase className="w-5 h-5 text-gray-600" />
              <span className="font-medium text-gray-700">Average Wage Effect</span>
            </div>
            <span className={`font-bold ${aggregate.avg_wage_effect > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {aggregate.avg_wage_effect > 0 ? '+' : ''}{aggregate.avg_wage_effect.toFixed(1)}%
            </span>
          </div>
        </div>
      )}

      {/* Data Source Info */}
      {results.data_source && (
        <div className={`rounded-xl shadow-md p-4 ${
          results.data_source.quality === 'research-grade'
            ? 'bg-green-50 border border-green-200'
            : 'bg-amber-50 border border-amber-200'
        }`}>
          <div className="flex items-start space-x-3">
            {results.data_source.quality === 'research-grade' ? (
              <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
            ) : (
              <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5" />
            )}
            <div>
              <div className="flex items-center space-x-2">
                <Database className="w-4 h-4 text-gray-500" />
                <span className="font-medium text-gray-700">Data Source: {results.data_source.multiplier_source}</span>
                {results.data_source.reference_year !== 'N/A' && (
                  <span className="text-xs text-gray-500">({results.data_source.reference_year})</span>
                )}
              </div>
              <p className="text-xs text-gray-600 mt-1">{results.data_source.notes}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ResultsPanel;
