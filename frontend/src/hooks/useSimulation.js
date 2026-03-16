import { useState, useCallback } from 'react';
import { runSimulation, explainResults } from '../services/api';

const DEFAULT_PARAMS = {
  country_code: 'ZAF',
  name: 'Custom Scenario',
  tariff_changes: {},
  subsidy_changes: {},
  sme_stimulus: 0,
  productivity_investment: 0,
  time_horizon: 'medium',
};

export function useSimulation() {
  const [params, setParams] = useState(DEFAULT_PARAMS);
  const [results, setResults] = useState(null);
  const [interpretation, setInterpretation] = useState(null);
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

  const updateSubsidy = useCallback((sector, value) => {
    setParams(prev => ({
      ...prev,
      subsidy_changes: {
        ...prev.subsidy_changes,
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
      setInterpretation(null);
      explainResults(result).then(resp => setInterpretation(resp.explanation)).catch(() => {});
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
    setInterpretation(null);
    setError(null);
  }, []);

  return {
    params,
    results,
    interpretation,
    loading,
    error,
    updateParam,
    updateTariff,
    updateSubsidy,
    simulate,
    loadPreset,
    reset,
  };
}

export default useSimulation;
