/**
 * API Service for Economic Policy Simulator
 */

const API_BASE = '/api';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const text = await response.text();
      let detail;
      try {
        detail = JSON.parse(text).detail;
      } catch {
        detail = `HTTP ${response.status}: ${text.substring(0, 200) || response.statusText}`;
      }
      throw new ApiError(detail || `Request failed (${response.status})`, response.status);
    }

    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(error.message || 'Network error - is the backend running?', 0);
  }
}

// ============== Simulation API ==============

export async function runSimulation(params) {
  return fetchApi('/simulate', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

export async function getMultipliers(countryCode) {
  return fetchApi(`/multipliers/${countryCode}`);
}

export async function getSectors() {
  return fetchApi('/sectors');
}

// ============== Country Data API ==============

export async function getCountries() {
  return fetchApi('/countries');
}

export async function getCountryProfile(countryCode, year = null) {
  const yearParam = year ? `?year=${year}` : '';
  return fetchApi(`/country/${countryCode}/profile${yearParam}`);
}

export async function getIndicators() {
  return fetchApi('/indicators');
}

export async function getTimeSeries(indicatorKey, countryCodes, startYear, endYear) {
  return fetchApi('/timeseries', {
    method: 'POST',
    body: JSON.stringify({
      indicator_key: indicatorKey,
      country_codes: countryCodes,
      start_year: startYear,
      end_year: endYear,
    }),
  });
}

export async function compareCountries(indicatorKey, startYear = 2015, endYear = 2024) {
  return fetchApi(`/comparison/${indicatorKey}?start_year=${startYear}&end_year=${endYear}`);
}

// ============== Chat/AI API ==============

export async function sendChatMessage(message, countryCode = 'ZAF', currentParams = null) {
  return fetchApi('/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      country_code: countryCode,
      current_params: currentParams,
    }),
  });
}

export async function explainResults(results, question = null) {
  return fetchApi('/explain', {
    method: 'POST',
    body: JSON.stringify(results),
  });
}

export async function suggestPolicies(countryCode, goal) {
  return fetchApi(`/suggest/${countryCode}?goal=${encodeURIComponent(goal)}`);
}

// ============== Presets API ==============

export async function getPresets(countryCode = null) {
  const param = countryCode ? `?country_code=${countryCode}` : '';
  return fetchApi(`/presets${param}`);
}

export async function getPreset(presetId) {
  return fetchApi(`/presets/${presetId}`);
}

// ============== Health Check ==============

export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE.replace('/api', '')}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

export { ApiError };
