import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, RefreshCw, Users, Briefcase, DollarSign, Globe } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { getCountryProfile, compareCountries } from '../services/api';

function CountryDashboard({ countryCode }) {
  const [profile, setProfile] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, [countryCode]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [profileData, comparisonData] = await Promise.all([
        getCountryProfile(countryCode),
        compareCountries('unemployment_total', 2010, 2024),
      ]);
      setProfile(profileData);
      setComparison(comparisonData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (trend) => {
    if (trend === 'increasing') return <TrendingUp className="w-4 h-4 text-red-500" />;
    if (trend === 'decreasing') return <TrendingDown className="w-4 h-4 text-green-500" />;
    return <Minus className="w-4 h-4 text-gray-400" />;
  };

  const formatValue = (value, unit) => {
    if (unit === 'people') {
      if (value >= 1e9) return `${(value / 1e9).toFixed(1)}B`;
      if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
      if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
      return value.toLocaleString();
    }
    if (unit === 'USD') {
      if (value >= 1e12) return `$${(value / 1e12).toFixed(1)}T`;
      if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
      if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
      return `$${value.toLocaleString()}`;
    }
    if (unit === '%') {
      return `${value.toFixed(1)}%`;
    }
    return value.toLocaleString();
  };

  // Prepare chart data
  const prepareChartData = () => {
    if (!comparison?.data) return [];

    const countries = ['ZAF', 'TUN', 'VNM', 'THA', 'SEN'];
    const yearMap = new Map();

    countries.forEach(code => {
      const countryData = comparison.data[code] || [];
      countryData.forEach(d => {
        const existing = yearMap.get(d.year) || { year: d.year };
        existing[code] = d.value;
        yearMap.set(d.year, existing);
      });
    });

    return Array.from(yearMap.values()).sort((a, b) => a.year - b.year);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-md p-8">
        <div className="flex items-center justify-center space-x-2">
          <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />
          <span className="text-gray-500">Loading country data from World Bank...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-md p-8">
        <div className="text-center text-red-500">
          <p>Error loading data: {error}</p>
          <button
            onClick={fetchData}
            className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const chartData = prepareChartData();

  return (
    <div className="space-y-4">
      {/* Country Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl shadow-md p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <span className="text-3xl">{{ 'ZAF': '🇿🇦', 'TUN': '🇹🇳', 'VNM': '🇻🇳', 'THA': '🇹🇭' }[countryCode] || '🌍'}</span>
              <h2 className="text-2xl font-bold">{profile?.country_name}</h2>
            </div>
            <p className="text-blue-200">{profile?.region}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-blue-200">Data Year</p>
            <p className="text-xl font-bold">{profile?.data_year}</p>
          </div>
        </div>
      </div>

      {/* Key Indicators Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Unemployment */}
        <div className="bg-white rounded-xl shadow-md p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Users className="w-5 h-5 text-red-500" />
            <span className="text-sm text-gray-600">Unemployment</span>
          </div>
          {profile?.indicators?.unemployment_total && (
            <>
              <div className="text-2xl font-bold text-gray-800">
                {formatValue(profile.indicators.unemployment_total.value, '%')}
              </div>
              <div className="flex items-center space-x-1 text-xs text-gray-500">
                {getTrendIcon(profile.indicators.unemployment_total.trend)}
                <span>{profile.indicators.unemployment_total.trend}</span>
              </div>
            </>
          )}
        </div>

        {/* Youth Unemployment */}
        <div className="bg-white rounded-xl shadow-md p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Users className="w-5 h-5 text-orange-500" />
            <span className="text-sm text-gray-600">Youth Unemployment</span>
          </div>
          {profile?.indicators?.unemployment_youth && (
            <>
              <div className="text-2xl font-bold text-gray-800">
                {formatValue(profile.indicators.unemployment_youth.value, '%')}
              </div>
              <div className="flex items-center space-x-1 text-xs text-gray-500">
                {getTrendIcon(profile.indicators.unemployment_youth.trend)}
                <span>Ages 15-24</span>
              </div>
            </>
          )}
        </div>

        {/* GDP */}
        <div className="bg-white rounded-xl shadow-md p-4">
          <div className="flex items-center space-x-2 mb-2">
            <DollarSign className="w-5 h-5 text-green-500" />
            <span className="text-sm text-gray-600">GDP</span>
          </div>
          {profile?.indicators?.gdp_current && (
            <>
              <div className="text-2xl font-bold text-gray-800">
                {formatValue(profile.indicators.gdp_current.value, 'USD')}
              </div>
              <div className="flex items-center space-x-1 text-xs text-gray-500">
                {getTrendIcon(profile.indicators.gdp_current.trend)}
                <span>Current USD</span>
              </div>
            </>
          )}
        </div>

        {/* Labor Force */}
        <div className="bg-white rounded-xl shadow-md p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Briefcase className="w-5 h-5 text-blue-500" />
            <span className="text-sm text-gray-600">Labor Force</span>
          </div>
          {profile?.indicators?.labor_force && (
            <>
              <div className="text-2xl font-bold text-gray-800">
                {formatValue(profile.indicators.labor_force.value, 'people')}
              </div>
              <div className="flex items-center space-x-1 text-xs text-gray-500">
                <span>Total workers</span>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Gender Breakdown */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="font-bold text-gray-800 mb-4">Employment by Gender</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-pink-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Female Unemployment</div>
            <div className="text-xl font-bold text-pink-700">
              {profile?.indicators?.unemployment_female
                ? formatValue(profile.indicators.unemployment_female.value, '%')
                : 'N/A'
              }
            </div>
          </div>
          <div className="p-4 bg-blue-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Male Unemployment</div>
            <div className="text-xl font-bold text-blue-700">
              {profile?.indicators?.unemployment_male
                ? formatValue(profile.indicators.unemployment_male.value, '%')
                : 'N/A'
              }
            </div>
          </div>
        </div>
      </div>

      {/* Sectoral Employment */}
      {profile?.indicators && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="font-bold text-gray-800 mb-4">Employment by Sector</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-700">
                {profile.indicators.empl_agriculture
                  ? formatValue(profile.indicators.empl_agriculture.value, '%')
                  : 'N/A'
                }
              </div>
              <div className="text-sm text-gray-600">Agriculture</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-700">
                {profile.indicators.empl_industry
                  ? formatValue(profile.indicators.empl_industry.value, '%')
                  : 'N/A'
                }
              </div>
              <div className="text-sm text-gray-600">Industry</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-700">
                {profile.indicators.empl_services
                  ? formatValue(profile.indicators.empl_services.value, '%')
                  : 'N/A'
                }
              </div>
              <div className="text-sm text-gray-600">Services</div>
            </div>
          </div>
        </div>
      )}

      {/* Unemployment Trend Chart */}
      {chartData.length > 0 && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="font-bold text-gray-800 mb-4">Unemployment Rate Comparison</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis unit="%" />
                <Tooltip formatter={(value) => [`${value?.toFixed(1)}%`, '']} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="ZAF"
                  name="South Africa"
                  stroke="#007749"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="TUN"
                  name="Tunisia"
                  stroke="#E70013"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="VNM"
                  name="Viet Nam"
                  stroke="#DA251D"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  strokeDasharray="5 5"
                />
                <Line
                  type="monotone"
                  dataKey="THA"
                  name="Thailand"
                  stroke="#241D4F"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  strokeDasharray="5 5"
                />
                <Line
                  type="monotone"
                  dataKey="SEN"
                  name="Senegal"
                  stroke="#00853F"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  strokeDasharray="3 3"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-gray-400 mt-2 text-center">
            Source: World Bank World Development Indicators (WDI)
          </p>
        </div>
      )}
    </div>
  );
}

export default CountryDashboard;
