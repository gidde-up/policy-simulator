import React, { useState } from 'react';
import { TrendingUp, TrendingDown, Briefcase, AlertCircle, HelpCircle, ArrowRight, Database, DollarSign, Scale, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';

// Helper component for before/after unemployment display
function UnemploymentIndicator({ label, icon, current, projected, change, color }) {
  const isImprovement = change < 0; // Negative change in unemployment is good
  const changeAbs = Math.abs(change);

  const colorClasses = {
    gray: { bg: 'bg-gray-100', text: 'text-gray-700' },
    blue: { bg: 'bg-blue-50', text: 'text-blue-700' },
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
        <div className="text-center flex-1">
          <div className="text-xs text-gray-500 mb-1">Current</div>
          <div className="text-2xl font-bold text-gray-800">{current.toFixed(1)}%</div>
        </div>
        <div className="flex flex-col items-center px-4">
          <ArrowRight className={`w-6 h-6 ${isImprovement ? 'text-green-500' : 'text-red-500'}`} />
          <span className={`text-xs font-medium mt-1 ${isImprovement ? 'text-green-600' : 'text-red-600'}`}>
            {isImprovement ? '-' : '+'}{changeAbs.toFixed(2)}pp
          </span>
        </div>
        <div className="text-center flex-1">
          <div className="text-xs text-gray-500 mb-1">Projected</div>
          <div className={`text-2xl font-bold ${isImprovement ? 'text-green-600' : 'text-red-600'}`}>
            {projected.toFixed(1)}%
          </div>
        </div>
      </div>
    </div>
  );
}

const CHANNEL_LABELS = {
  protected_sector_gain: { label: 'Protected-sector gain', hint: 'Import substitution into the tariffed sector' },
  downstream_cost: { label: 'Downstream cost', hint: 'Higher input costs reduce demand for downstream output (incl. exports)' },
  real_income_loss: { label: 'Real-income loss', hint: 'Consumer prices rise; household demand falls across all sectors' },
  retaliation: { label: 'Retaliation (stylised)', hint: 'Export demand falls in top export sectors' },
  sector_support: { label: 'Sector support', hint: 'Government spending boosts demand for the supported sector' },
  financing_drag: { label: 'Financing drag', hint: 'Tax-financed: household consumption falls by the spending amount' },
  sme_stimulus: { label: 'Demand stimulus', hint: 'Stimulus spread through household consumption' },
};

function ChannelBar({ name, jobs, maxAbs }) {
  const meta = CHANNEL_LABELS[name] || { label: name, hint: '' };
  const positive = jobs >= 0;
  const width = maxAbs > 0 ? Math.max(2, (Math.abs(jobs) / maxAbs) * 100) : 0;
  return (
    <div className="mb-2" title={meta.hint}>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-600">{meta.label}</span>
        <span className={`font-medium ${positive ? 'text-green-700' : 'text-red-700'}`}>
          {positive ? '+' : ''}{Math.round(jobs).toLocaleString()} jobs
        </span>
      </div>
      <div className="bg-gray-100 rounded h-3 overflow-hidden">
        <div
          className={`h-3 ${positive ? 'bg-green-500' : 'bg-red-500'}`}
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  );
}

function ResultsPanel({ results, loading }) {
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

  const { aggregate, sector_effects, tariff_channels, other_channels, costs, uncertainty, data_source, baseline, induced_note } = results;
  const totalJobs = aggregate.total_jobs;
  const isPositive = totalJobs > 0;

  // gross reallocation: the robust message when the net is marginal
  const grossGains = sector_effects.reduce(
    (acc, s) => acc + Math.max(0, s.total_jobs), 0);
  const grossLosses = sector_effects.reduce(
    (acc, s) => acc + Math.min(0, s.total_jobs), 0);

  // "approximately zero" framing: the parameter range straddles zero,
  // or the net effect is below 0.05% of baseline employment
  const rangeStraddlesZero = uncertainty.low < 0 && uncertainty.high > 0;
  const nearZero = rangeStraddlesZero
    || Math.abs(aggregate.pct_of_baseline_employment) < 0.05;

  // channel bars: merge tariff + other channels, drop nulls
  const channelEntries = [];
  if (tariff_channels) {
    for (const [k, v] of Object.entries(tariff_channels)) {
      if (v) channelEntries.push([k, v.jobs]);
    }
  }
  if (other_channels) {
    for (const [k, v] of Object.entries(other_channels)) {
      if (v) channelEntries.push([k, v.jobs]);
    }
  }
  const maxAbsChannel = Math.max(...channelEntries.map(([, j]) => Math.abs(j)), 0);

  // sector chart data
  const sectorData = sector_effects
    .map(se => ({
      name: se.sector.replace(/_/g, ' '),
      total: Math.round(se.total_jobs),
    }))
    .sort((a, b) => b.total - a.total);

  return (
    <div className="space-y-6">
      {/* Model boundaries warning */}
      {!warningDismissed && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1 text-sm text-amber-800">
            <span className="font-medium">Learning tool, not a forecast.</span>{' '}
            Comparative-static, demand-driven input-output results at fixed prices and
            technology: no exchange-rate effects, no supply constraints, no dynamics.
            Read direction and rough magnitude, not point predictions.
          </div>
          <button
            onClick={() => setWarningDismissed(true)}
            className="text-amber-500 hover:text-amber-700 text-sm font-medium"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Employment Impact Summary */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-800 flex items-center">
            <Briefcase className="w-5 h-5 mr-2 text-blue-600" />
            Employment Impact
          </h2>
          <span className="text-xs text-gray-500">
            Comparative-static adjustment
          </span>
        </div>

        {nearZero ? (
          /* marginal net result: the honest headline is the reallocation */
          <div className="mb-2">
            <div className="text-3xl font-bold text-gray-800">
              Net effect: approximately zero
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Point estimate {totalJobs >= 0 ? '+' : ''}{Math.round(totalJobs).toLocaleString()} jobs
              ({aggregate.pct_of_baseline_employment >= 0 ? '+' : ''}
              {aggregate.pct_of_baseline_employment.toFixed(3)}% of baseline employment)
              {rangeStraddlesZero && ' - the parameter range includes both signs'}
            </div>
            <div className="text-base font-medium text-gray-800 mt-2">
              The robust result is the reallocation:{' '}
              <span className="text-green-700">+{Math.round(grossGains).toLocaleString()}</span>
              {' / '}
              <span className="text-red-700">{Math.round(grossLosses).toLocaleString()}</span>
              {' '}jobs shifted between sectors
            </div>
          </div>
        ) : (
          <div className="flex items-center space-x-4 mb-2">
            {isPositive ? (
              <TrendingUp className="w-10 h-10 text-green-600" />
            ) : (
              <TrendingDown className="w-10 h-10 text-red-600" />
            )}
            <div>
              <div className={`text-4xl font-bold ${isPositive ? 'text-green-700' : 'text-red-700'}`}>
                {isPositive ? '+' : ''}{Math.round(totalJobs).toLocaleString()} jobs
              </div>
              <div className="text-sm text-gray-600">
                {aggregate.pct_of_baseline_employment >= 0 ? '+' : ''}
                {aggregate.pct_of_baseline_employment.toFixed(3)}% of baseline employment
                ({Math.round(baseline.sector_sum_employment_persons).toLocaleString()} persons, {baseline.reference_year})
                {' '}&middot; gross: <span className="text-green-700">+{Math.round(grossGains).toLocaleString()}</span>
                {' / '}<span className="text-red-700">{Math.round(grossLosses).toLocaleString()}</span>
              </div>
            </div>
          </div>
        )}

        <div className="text-sm text-gray-700 bg-gray-50 rounded-lg p-3 mb-4">
          Range over the registered parameter values:{' '}
          <span className="font-medium">
            {Math.round(uncertainty.low).toLocaleString()} to {Math.round(uncertainty.high).toLocaleString()} jobs
          </span>
          <span className="text-xs text-gray-500 block mt-1">{uncertainty.basis}</span>
        </div>

        {/* Direct / indirect / induced breakdown */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-blue-50 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500 mb-1">Direct</div>
            <div className="text-xl font-bold text-blue-700">
              {Math.round(aggregate.direct_jobs).toLocaleString()}
            </div>
          </div>
          <div className="bg-indigo-50 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500 mb-1">Indirect (supply chain)</div>
            <div className="text-xl font-bold text-indigo-700">
              {Math.round(aggregate.indirect_jobs).toLocaleString()}
            </div>
          </div>
          <div className="bg-purple-50 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500 mb-1">Induced (Type II)</div>
            <div className="text-xl font-bold text-purple-700">
              {aggregate.induced_jobs !== null && aggregate.induced_jobs !== undefined
                ? Math.round(aggregate.induced_jobs).toLocaleString()
                : 'off'}
            </div>
          </div>
        </div>
        {induced_note && (
          <p className="text-xs text-purple-600 mt-2">{induced_note}</p>
        )}
      </div>

      {/* Channel decomposition */}
      {channelEntries.length > 0 && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-1 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-blue-600" />
            Transmission Channels
          </h3>
          <p className="text-xs text-gray-500 mb-4">
            How the policy reaches employment: the bars sum to the net effect.
          </p>
          {channelEntries.map(([name, jobs]) => (
            <ChannelBar key={name} name={name} jobs={jobs} maxAbs={maxAbsChannel} />
          ))}
        </div>
      )}

      {/* Sector chart */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Employment Change by Sector</h3>
        <ResponsiveContainer width="100%" height={420}>
          <BarChart data={sectorData} layout="vertical" margin={{ left: 30 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" tickFormatter={(v) => v.toLocaleString()} />
            <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 12 }} />
            <Tooltip formatter={(v) => [`${v.toLocaleString()} jobs`, 'Total']} />
            <ReferenceLine x={0} stroke="#9ca3af" />
            <Bar dataKey="total">
              {sectorData.map((entry, i) => (
                <Cell key={i} fill={entry.total >= 0 ? '#22c55e' : '#ef4444'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Costs */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
          <Scale className="w-5 h-5 mr-2 text-blue-600" />
          Fiscal Flows (USD million / year)
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">Tariff revenue</div>
            <div className="text-lg font-bold text-gray-800">
              {Math.round(costs.tariff_revenue_usd_million).toLocaleString()}
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">Spending</div>
            <div className="text-lg font-bold text-gray-800">
              {Math.round(costs.spending_cost_usd_million).toLocaleString()}
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">Net fiscal</div>
            <div className={`text-lg font-bold ${costs.net_fiscal_usd_million >= 0 ? 'text-green-700' : 'text-red-700'}`}>
              {Math.round(costs.net_fiscal_usd_million).toLocaleString()}
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">Fiscal cost / job</div>
            <div className="text-lg font-bold text-gray-800">
              {costs.cost_per_job_fiscal_usd
                ? `$${Math.round(costs.cost_per_job_fiscal_usd).toLocaleString()}`
                : 'n/a'}
            </div>
          </div>
        </div>
        {costs.financing_drag_included && (
          <p className="text-xs text-gray-500 mt-2 flex items-center">
            <DollarSign className="w-3 h-3 mr-1" />
            Sector support is modelled as tax-financed (financing drag included).
          </p>
        )}
      </div>

      {/* WDI unemployment baseline */}
      {results.baseline_indicators?.unemployment_total && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Unemployment Context (World Bank WDI)</h3>
          <UnemploymentIndicator
            label="Total Unemployment Rate"
            icon={<Activity className="w-4 h-4" />}
            current={results.baseline_indicators.unemployment_total.current_value}
            projected={results.baseline_indicators.unemployment_total.projected_value}
            change={results.baseline_indicators.unemployment_total.change}
            color="blue"
          />
          <p className="text-xs text-gray-500 mt-2">
            Projection applies the simulated net job change to the WDI labour force;
            the WDI (LFS) employment concept differs from the model baseline.
          </p>
        </div>
      )}

      {/* Data source + model version stamp */}
      <div className="bg-white rounded-xl shadow-md p-4 flex items-start space-x-3">
        <Database className="w-5 h-5 text-gray-500 mt-0.5 flex-shrink-0" />
        <div className="text-xs text-gray-600">
          <span className="font-medium text-gray-700">
            {data_source.model_version ? `Model v${data_source.model_version} - ` : ''}
            {data_source.citation}
          </span>
          <span className="block mt-1">
            Behavioural parameters: {results.assumptions_used.join(', ')} (see assumptions registry).
          </span>
        </div>
      </div>
    </div>
  );
}

export default ResultsPanel;
