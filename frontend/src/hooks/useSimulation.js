import { useState, useCallback } from 'react';
import { runSimulation } from '../services/api';

const DEFAULT_PARAMS = {
  country_code: 'ZAF',
  name: 'Custom Scenario',
  tariff_changes: {},
  sector_support: {},
  sme_stimulus: 0,
  include_type_ii: false,
  include_retaliation: false,
  include_financing_drag: true,
  // extension levers (Session F/H)
  production_subsidy: {},
  wage_subsidy: {},
  stimulus_target: 'household',
  public_investment: null,          // {amount_pct_gdp, target}
  investment_tax_incentive: null,   // {fiscal_cost_pct_gdp, intensity, target}
  public_works: null,               // {budget_pct_gdp, method}
  direct_public_employment: null,   // {budget_pct_gdp}
  depreciation: 0,
};

export function useSimulation() {
  const [params, setParams] = useState(DEFAULT_PARAMS);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const updateParam = useCallback((key, value) => {
    setParams(prev => ({ ...prev, [key]: value }));
  }, []);

  const updateTariff = useCallback((sector, value) => {
    setParams(prev => ({
      ...prev,
      tariff_changes: {
        ...prev.tariff_changes,
        [sector]: value,
      },
    }));
  }, []);

  const updateSupport = useCallback((sector, value) => {
    setParams(prev => ({
      ...prev,
      sector_support: { ...prev.sector_support, [sector]: value },
    }));
  }, []);

  // generic per-sector setter for the subsidy dict levers
  const updateSectorMap = useCallback((key, sector, value) => {
    setParams(prev => ({
      ...prev,
      [key]: { ...(prev[key] || {}), [sector]: value },
    }));
  }, []);

  const simulate = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await runSimulation(params);
      setResults(result);
      return result;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, [params]);

  const loadPreset = useCallback((presetParams) => {
    setParams({
      ...DEFAULT_PARAMS,
      ...presetParams,
    });
  }, []);

  const reset = useCallback(() => {
    setParams(DEFAULT_PARAMS);
    setResults(null);
    setError(null);
  }, []);

  return {
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
  };
}

export default useSimulation;
