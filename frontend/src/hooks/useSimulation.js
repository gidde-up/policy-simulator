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
      sector_support: {
        ...prev.sector_support,
        [sector]: value,
      },
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
    simulate,
    loadPreset,
    reset,
  };
}

export default useSimulation;
