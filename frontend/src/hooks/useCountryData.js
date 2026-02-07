import { useState, useEffect, useCallback } from 'react';
import { getCountryProfile, getTimeSeries } from '../services/api';

export function useCountryData(countryCode) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchProfile = useCallback(async () => {
    if (!countryCode) return;

    setLoading(true);
    setError(null);

    try {
      const data = await getCountryProfile(countryCode);
      setProfile(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [countryCode]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const fetchTimeSeries = useCallback(async (indicator, startYear = 2010, endYear = 2024) => {
    try {
      return await getTimeSeries(indicator, [countryCode], startYear, endYear);
    } catch (err) {
      console.error('Error fetching time series:', err);
      return null;
    }
  }, [countryCode]);

  return {
    profile,
    loading,
    error,
    refresh: fetchProfile,
    fetchTimeSeries,
  };
}

export default useCountryData;
