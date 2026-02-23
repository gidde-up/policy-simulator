import React from 'react';
import { Globe, Info, HelpCircle } from 'lucide-react';

function Header({ selectedCountry, onCountryChange }) {
  const countries = [
    { code: 'ZAF', name: 'South Africa', flag: '🇿🇦' },
    { code: 'TUN', name: 'Tunisia', flag: '🇹🇳' },
    { code: 'VNM', name: 'Viet Nam', flag: '🇻🇳' },
    { code: 'THA', name: 'Thailand', flag: '🇹🇭' },
    { code: 'MOZ', name: 'Mozambique', flag: '🇲🇿' },
  ];

  return (
    <header className="gradient-bg text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Globe className="w-8 h-8 text-wb-light" />
            <div>
              <h1 className="text-xl font-bold">Economic Policy Simulator</h1>
              <p className="text-sm text-blue-200">Job Creation Analysis Tool</p>
            </div>
          </div>

          <div className="flex items-center space-x-6">
            {/* Country Selector */}
            <div className="flex items-center space-x-2">
              <span className="text-sm text-blue-200">Country:</span>
              <div className="flex bg-white/10 rounded-lg p-1">
                {countries.map((country) => (
                  <button
                    key={country.code}
                    onClick={() => onCountryChange(country.code)}
                    className={`
                      px-4 py-2 rounded-md text-sm font-medium transition-all
                      ${selectedCountry === country.code
                        ? 'bg-white text-wb-blue'
                        : 'text-white hover:bg-white/10'
                      }
                    `}
                  >
                    <span className="mr-2 text-lg emoji-text">{country.flag}</span>
                    <span>{country.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Info button */}
            <button
              className="p-2 rounded-full hover:bg-white/10 transition-colors"
              title="About this tool"
            >
              <Info className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Subtitle bar */}
      <div className="bg-black/20 py-2">
        <div className="max-w-7xl mx-auto px-4">
          <p className="text-sm text-blue-100 flex items-center">
            <HelpCircle className="w-4 h-4 mr-2" />
            Explore how economic policies affect job creation. Adjust policy levers below and see projected employment impacts.
          </p>
        </div>
      </div>
    </header>
  );
}

export default Header;
