"""
World Bank WDI API Service
===========================
Fetches real economic data from the World Development Indicators API.

API Documentation: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
"""

import httpx
from typing import Dict, List, Optional, Any
from cachetools import TTLCache
import asyncio
from dataclasses import dataclass
from datetime import datetime


# Cache for API responses (1 hour TTL)
_cache = TTLCache(maxsize=100, ttl=3600)


@dataclass
class WDIIndicator:
    """Represents a WDI indicator configuration"""
    code: str
    name: str
    description: str
    unit: str


# Key indicators for employment analysis
INDICATORS = {
    # Employment
    'employment_ratio': WDIIndicator(
        'SL.EMP.TOTL.SP.ZS',
        'Employment to population ratio',
        'Employment to population ratio, 15+, total (%) (modeled ILO estimate)',
        '%'
    ),
    'employment_ratio_female': WDIIndicator(
        'SL.EMP.TOTL.SP.FE.ZS',
        'Employment ratio (female)',
        'Employment to population ratio, 15+, female (%) (modeled ILO estimate)',
        '%'
    ),
    'employment_ratio_male': WDIIndicator(
        'SL.EMP.TOTL.SP.MA.ZS',
        'Employment ratio (male)',
        'Employment to population ratio, 15+, male (%) (modeled ILO estimate)',
        '%'
    ),

    # Unemployment
    'unemployment_total': WDIIndicator(
        'SL.UEM.TOTL.ZS',
        'Unemployment rate',
        'Unemployment, total (% of total labor force) (modeled ILO estimate)',
        '%'
    ),
    'unemployment_female': WDIIndicator(
        'SL.UEM.TOTL.FE.ZS',
        'Unemployment rate (female)',
        'Unemployment, female (% of female labor force) (modeled ILO estimate)',
        '%'
    ),
    'unemployment_male': WDIIndicator(
        'SL.UEM.TOTL.MA.ZS',
        'Unemployment rate (male)',
        'Unemployment, male (% of male labor force) (modeled ILO estimate)',
        '%'
    ),
    'unemployment_youth': WDIIndicator(
        'SL.UEM.1524.ZS',
        'Youth unemployment rate',
        'Unemployment, youth total (% of total labor force ages 15-24) (modeled ILO estimate)',
        '%'
    ),
    'unemployment_youth_female': WDIIndicator(
        'SL.UEM.1524.FE.ZS',
        'Youth unemployment rate (female)',
        'Unemployment, youth female (% of female labor force ages 15-24)',
        '%'
    ),
    'unemployment_youth_male': WDIIndicator(
        'SL.UEM.1524.MA.ZS',
        'Youth unemployment rate (male)',
        'Unemployment, youth male (% of male labor force ages 15-24)',
        '%'
    ),

    # Labor force participation
    'lfp_total': WDIIndicator(
        'SL.TLF.CACT.ZS',
        'Labor force participation rate',
        'Labor force participation rate, total (% of total population ages 15+) (modeled ILO estimate)',
        '%'
    ),
    'lfp_female': WDIIndicator(
        'SL.TLF.CACT.FE.ZS',
        'Labor force participation (female)',
        'Labor force participation rate, female (% of female population ages 15+)',
        '%'
    ),
    'lfp_male': WDIIndicator(
        'SL.TLF.CACT.MA.ZS',
        'Labor force participation (male)',
        'Labor force participation rate, male (% of male population ages 15+)',
        '%'
    ),

    # Sectoral employment
    'empl_agriculture': WDIIndicator(
        'SL.AGR.EMPL.ZS',
        'Employment in agriculture',
        'Employment in agriculture (% of total employment) (modeled ILO estimate)',
        '%'
    ),
    'empl_industry': WDIIndicator(
        'SL.IND.EMPL.ZS',
        'Employment in industry',
        'Employment in industry (% of total employment) (modeled ILO estimate)',
        '%'
    ),
    'empl_services': WDIIndicator(
        'SL.SRV.EMPL.ZS',
        'Employment in services',
        'Employment in services (% of total employment) (modeled ILO estimate)',
        '%'
    ),

    # Economic indicators
    'gdp_current': WDIIndicator(
        'NY.GDP.MKTP.CD',
        'GDP (current US$)',
        'Gross domestic product at current US dollars',
        'USD'
    ),
    'gdp_growth': WDIIndicator(
        'NY.GDP.MKTP.KD.ZG',
        'GDP growth',
        'GDP growth (annual %)',
        '%'
    ),
    'gdp_per_capita': WDIIndicator(
        'NY.GDP.PCAP.CD',
        'GDP per capita',
        'GDP per capita (current US$)',
        'USD'
    ),

    # Trade indicators
    'trade_pct_gdp': WDIIndicator(
        'NE.TRD.GNFS.ZS',
        'Trade (% of GDP)',
        'Trade is the sum of exports and imports of goods and services measured as a share of GDP',
        '%'
    ),
    'exports_pct_gdp': WDIIndicator(
        'NE.EXP.GNFS.ZS',
        'Exports (% of GDP)',
        'Exports of goods and services (% of GDP)',
        '%'
    ),
    'imports_pct_gdp': WDIIndicator(
        'NE.IMP.GNFS.ZS',
        'Imports (% of GDP)',
        'Imports of goods and services (% of GDP)',
        '%'
    ),
    'tariff_rate': WDIIndicator(
        'TM.TAX.MRCH.WM.AR.ZS',
        'Tariff rate, applied, weighted mean',
        'Tariff rate, applied, weighted mean, all products (%)',
        '%'
    ),

    # Population
    'population': WDIIndicator(
        'SP.POP.TOTL',
        'Population',
        'Total population',
        'people'
    ),
    'labor_force': WDIIndicator(
        'SL.TLF.TOTL.IN',
        'Labor force, total',
        'Labor force, total',
        'people'
    ),

    # Vulnerable employment
    'vulnerable_employment': WDIIndicator(
        'SL.EMP.VULN.ZS',
        'Vulnerable employment',
        'Vulnerable employment, total (% of total employment) (modeled ILO estimate)',
        '%'
    ),
    'vulnerable_employment_female': WDIIndicator(
        'SL.EMP.VULN.FE.ZS',
        'Vulnerable employment (female)',
        'Vulnerable employment, female (% of female employment)',
        '%'
    ),

    # Wage and salaried workers
    'wage_workers': WDIIndicator(
        'SL.EMP.WORK.ZS',
        'Wage and salaried workers',
        'Wage and salaried workers, total (% of total employment)',
        '%'
    ),
    'wage_workers_female': WDIIndicator(
        'SL.EMP.WORK.FE.ZS',
        'Wage workers (female)',
        'Wage and salaried workers, female (% of female employment)',
        '%'
    ),

    # Government expenditure
    'gov_expenditure': WDIIndicator(
        'NE.CON.GOVT.ZS',
        'Government expenditure (% of GDP)',
        'General government final consumption expenditure (% of GDP)',
        '%'
    ),
}


class WDIService:
    """Service for fetching World Bank WDI data"""

    BASE_URL = "https://api.worldbank.org/v2"
    SUPPORTED_COUNTRIES = {
        'ZAF': {'name': 'South Africa', 'region': 'Sub-Saharan Africa'},
        'TUN': {'name': 'Tunisia', 'region': 'Middle East & North Africa'},
        'VNM': {'name': 'Viet Nam', 'region': 'East Asia & Pacific'},
        'THA': {'name': 'Thailand', 'region': 'East Asia & Pacific'},
        'MOZ': {'name': 'Mozambique', 'region': 'Sub-Saharan Africa'},
    }

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        await self.client.aclose()

    async def fetch_indicator(
        self,
        indicator_code: str,
        country_codes: List[str],
        start_year: int = 2010,
        end_year: int = 2024
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch indicator data for specified countries and time range.

        Returns dict keyed by country code with list of yearly values.
        """
        cache_key = f"{indicator_code}_{','.join(country_codes)}_{start_year}_{end_year}"

        if cache_key in _cache:
            return _cache[cache_key]

        countries = ";".join(country_codes)
        url = f"{self.BASE_URL}/country/{countries}/indicator/{indicator_code}"
        params = {
            'format': 'json',
            'date': f"{start_year}:{end_year}",
            'per_page': 500
        }

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # WDI API returns [metadata, data] array
            if not data or len(data) < 2:
                return {}

            records = data[1] or []

            # Organize by country
            result = {code: [] for code in country_codes}
            for record in records:
                if record['value'] is not None:
                    country = record['countryiso3code']
                    if country in result:
                        result[country].append({
                            'year': int(record['date']),
                            'value': record['value'],
                            'indicator': record['indicator']['id'],
                            'indicator_name': record['indicator']['value']
                        })

            # Sort by year
            for country in result:
                result[country].sort(key=lambda x: x['year'])

            _cache[cache_key] = result
            return result

        except httpx.HTTPError as e:
            print(f"WDI API error: {e}")
            return {}

    async def fetch_multiple_indicators(
        self,
        indicator_keys: List[str],
        country_codes: List[str],
        start_year: int = 2010,
        end_year: int = 2024
    ) -> Dict[str, Dict[str, List[Dict]]]:
        """
        Fetch multiple indicators in small batches to avoid WDI API rate limits.

        Returns nested dict: {indicator_key: {country_code: [values]}}
        """
        valid_keys = [k for k in indicator_keys if k in INDICATORS]
        output = {}

        # Fetch in batches of 5 to avoid rate limiting
        batch_size = 5
        for i in range(0, len(valid_keys), batch_size):
            batch_keys = valid_keys[i:i + batch_size]
            tasks = []
            for key in batch_keys:
                indicator = INDICATORS[key]
                tasks.append(
                    self.fetch_indicator(
                        indicator.code,
                        country_codes,
                        start_year,
                        end_year
                    )
                )

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for key, result in zip(batch_keys, results):
                if isinstance(result, Exception):
                    output[key] = {}
                else:
                    output[key] = result

            # Delay between batches to respect WDI API rate limits
            if i + batch_size < len(valid_keys):
                await asyncio.sleep(0.5)

        return output

    async def get_country_profile(
        self,
        country_code: str,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive country employment profile.

        Returns latest available data for key indicators.
        """
        if country_code not in self.SUPPORTED_COUNTRIES:
            return {'error': f'Country {country_code} not supported'}

        # Key indicators for profile
        profile_indicators = [
            'unemployment_total', 'unemployment_female', 'unemployment_male',
            'unemployment_youth', 'employment_ratio', 'lfp_total', 'lfp_female',
            'empl_agriculture', 'empl_industry', 'empl_services',
            'gdp_current', 'gdp_growth', 'gdp_per_capita',
            'population', 'labor_force',
            'vulnerable_employment', 'wage_workers',
            'gov_expenditure'
        ]

        end_year = year or datetime.now().year
        start_year = end_year - 5  # Get 5 years for trends

        data = await self.fetch_multiple_indicators(
            profile_indicators,
            [country_code],
            start_year,
            end_year
        )

        profile = {
            'country_code': country_code,
            'country_name': self.SUPPORTED_COUNTRIES[country_code]['name'],
            'region': self.SUPPORTED_COUNTRIES[country_code]['region'],
            'indicators': {},
            'data_year': None,
            'data_warnings': []
        }

        # Extract latest value for each indicator; flag any that are missing
        for key, country_data in data.items():
            if country_code in country_data and country_data[country_code]:
                values = country_data[country_code]
                latest = values[-1]  # Already sorted by year
                profile['indicators'][key] = {
                    'value': latest['value'],
                    'year': latest['year'],
                    'name': INDICATORS[key].name if key in INDICATORS else key,
                    'unit': INDICATORS[key].unit if key in INDICATORS else '',
                    'trend': self._calculate_trend(values)
                }
                if profile['data_year'] is None or latest['year'] > profile['data_year']:
                    profile['data_year'] = latest['year']
            else:
                indicator_name = INDICATORS[key].name if key in INDICATORS else key
                profile['data_warnings'].append(
                    f"'{indicator_name}' not available for {country_code} in WDI"
                )

        return profile

    async def get_time_series(
        self,
        indicator_key: str,
        country_codes: List[str],
        start_year: int = 2000,
        end_year: int = 2024
    ) -> Dict[str, Any]:
        """Get time series data for charting"""
        if indicator_key not in INDICATORS:
            return {'error': f'Unknown indicator: {indicator_key}'}

        indicator = INDICATORS[indicator_key]
        data = await self.fetch_indicator(
            indicator.code,
            country_codes,
            start_year,
            end_year
        )

        return {
            'indicator': {
                'code': indicator.code,
                'name': indicator.name,
                'description': indicator.description,
                'unit': indicator.unit
            },
            'data': data
        }

    def _calculate_trend(self, values: List[Dict]) -> str:
        """Calculate simple trend direction from time series"""
        if len(values) < 2:
            return 'stable'

        first = values[0]['value']
        last = values[-1]['value']

        if first == 0:
            return 'stable'

        change_pct = (last - first) / abs(first) * 100

        if change_pct > 5:
            return 'increasing'
        elif change_pct < -5:
            return 'decreasing'
        else:
            return 'stable'

    def get_available_indicators(self) -> Dict[str, Dict]:
        """Return list of available indicators with metadata"""
        return {
            key: {
                'code': ind.code,
                'name': ind.name,
                'description': ind.description,
                'unit': ind.unit
            }
            for key, ind in INDICATORS.items()
        }

    def get_supported_countries(self) -> Dict[str, Dict]:
        """Return supported countries"""
        return self.SUPPORTED_COUNTRIES.copy()


# Singleton instance
_service_instance = None


def get_wdi_service() -> WDIService:
    """Get WDI service singleton"""
    global _service_instance
    if _service_instance is None:
        _service_instance = WDIService()
    return _service_instance
