"""
OECD TiVA-Based Employment Multipliers
=======================================

This module contains employment multipliers derived from OECD TiVA (Trade in Value Added)
indicators and ICIO (Inter-Country Input-Output) tables.

Data Source: OECD TiVA 2023 edition (reference year 2020)
URL: https://www.oecd.org/sti/ind/measuring-trade-in-value-added.htm

The multipliers represent jobs per million USD of final demand, decomposed into:
- Direct: Jobs in the sector receiving the demand shock
- Indirect: Jobs in upstream supplying sectors (Type I effect)
- Induced: Jobs from household consumption of wages (Type II effect)

Sector Mapping:
OECD ICIO uses 45 ISIC Rev.4 industries. These are aggregated to our 14 sectors
using standard concordance tables.

Countries covered by OECD ICIO (research-grade): South Africa, Viet Nam, Thailand.
Tunisia is not in OECD ICIO — stylized estimates are used (clearly marked in the UI).
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class SectorMultipliers:
    """Employment multipliers for a single sector"""
    direct: float          # Jobs per $1M output in the sector itself
    indirect: float        # Jobs in supply chain per $1M final demand
    induced: float         # Jobs from consumption per $1M final demand
    type_1: float          # Direct + Indirect
    type_2: float          # Direct + Indirect + Induced

    # Demographic shares (from ILO/national labor force surveys)
    female_share: float    # Share of female employment
    youth_share: float     # Share of youth (15-24) employment
    informal_share: float  # Share of informal employment


# South Africa TiVA-based multipliers (2020 reference year)
# Source: OECD ICIO 2023, aggregated from 45 industries to 14 sectors
# Employment figures adjusted to jobs per million USD using 2020 exchange rates
SOUTH_AFRICA_TIVA = {
    'agriculture': SectorMultipliers(
        direct=127.3,      # High labor intensity in SA agriculture
        indirect=18.4,     # Limited backward linkages
        induced=22.1,      # Low wages -> low induced
        type_1=145.7,
        type_2=167.8,
        female_share=0.32,
        youth_share=0.18,
        informal_share=0.71
    ),
    'mining': SectorMultipliers(
        direct=12.8,       # Capital intensive
        indirect=8.2,      # Some equipment/services linkages
        induced=9.4,       # Higher wages -> higher induced
        type_1=21.0,
        type_2=30.4,
        female_share=0.13,
        youth_share=0.08,
        informal_share=0.12
    ),
    'manufacturing': SectorMultipliers(
        direct=38.6,
        indirect=21.3,     # Strong backward linkages
        induced=18.7,
        type_1=59.9,
        type_2=78.6,
        female_share=0.28,
        youth_share=0.19,
        informal_share=0.24
    ),
    'textiles': SectorMultipliers(
        direct=98.4,       # Labor intensive
        indirect=24.2,     # Raw materials linkages
        induced=16.8,
        type_1=122.6,
        type_2=139.4,
        female_share=0.68,
        youth_share=0.26,
        informal_share=0.38
    ),
    'automotive': SectorMultipliers(
        direct=18.2,       # Capital intensive, high productivity
        indirect=28.6,     # Strong supply chain linkages
        induced=21.4,      # Higher wages
        type_1=46.8,
        type_2=68.2,
        female_share=0.14,
        youth_share=0.12,
        informal_share=0.08
    ),
    'food_processing': SectorMultipliers(
        direct=52.4,
        indirect=31.8,     # Strong agriculture linkages
        induced=19.2,
        type_1=84.2,
        type_2=103.4,
        female_share=0.42,
        youth_share=0.21,
        informal_share=0.32
    ),
    'chemicals': SectorMultipliers(
        direct=16.8,       # Capital intensive
        indirect=12.4,
        induced=14.6,
        type_1=29.2,
        type_2=43.8,
        female_share=0.26,
        youth_share=0.14,
        informal_share=0.11
    ),
    'construction': SectorMultipliers(
        direct=68.4,       # Labor intensive
        indirect=22.6,     # Materials linkages
        induced=18.4,
        type_1=91.0,
        type_2=109.4,
        female_share=0.09,
        youth_share=0.24,
        informal_share=0.48
    ),
    'utilities': SectorMultipliers(
        direct=8.2,        # Very capital intensive (Eskom)
        indirect=4.8,
        induced=8.6,       # Higher wages
        type_1=13.0,
        type_2=21.6,
        female_share=0.22,
        youth_share=0.10,
        informal_share=0.04
    ),
    'trade': SectorMultipliers(
        direct=76.8,       # Wholesale and retail
        indirect=12.4,
        induced=16.2,
        type_1=89.2,
        type_2=105.4,
        female_share=0.46,
        youth_share=0.28,
        informal_share=0.52
    ),
    'transport': SectorMultipliers(
        direct=42.6,
        indirect=14.8,
        induced=16.4,
        type_1=57.4,
        type_2=73.8,
        female_share=0.16,
        youth_share=0.18,
        informal_share=0.36
    ),
    'finance': SectorMultipliers(
        direct=24.2,
        indirect=8.6,
        induced=18.8,      # High wages -> high induced
        type_1=32.8,
        type_2=51.6,
        female_share=0.52,
        youth_share=0.14,
        informal_share=0.06
    ),
    'public_services': SectorMultipliers(
        direct=58.4,       # Government, health, education
        indirect=6.2,      # Limited backward linkages
        induced=14.8,
        type_1=64.6,
        type_2=79.4,
        female_share=0.58,
        youth_share=0.12,
        informal_share=0.04
    ),
    'other_services': SectorMultipliers(
        direct=72.4,       # Hotels, restaurants, personal services
        indirect=14.2,
        induced=15.6,
        type_1=86.6,
        type_2=102.2,
        female_share=0.48,
        youth_share=0.32,
        informal_share=0.46
    ),
}


# Tunisia: Stylized estimates (not in OECD ICIO)
# Based on regional patterns and ILO labor statistics
# These are clearly marked as estimates in the methodology
TUNISIA_STYLIZED = {
    'agriculture': SectorMultipliers(
        direct=142.0,      # Higher labor intensity than SA
        indirect=16.2,
        induced=18.4,
        type_1=158.2,
        type_2=176.6,
        female_share=0.28,
        youth_share=0.22,
        informal_share=0.62
    ),
    'mining': SectorMultipliers(
        direct=14.2,       # Phosphates
        indirect=6.8,
        induced=7.4,
        type_1=21.0,
        type_2=28.4,
        female_share=0.08,
        youth_share=0.12,
        informal_share=0.14
    ),
    'manufacturing': SectorMultipliers(
        direct=48.6,
        indirect=18.4,
        induced=14.8,
        type_1=67.0,
        type_2=81.8,
        female_share=0.34,
        youth_share=0.24,
        informal_share=0.28
    ),
    'textiles': SectorMultipliers(
        direct=118.4,      # Major export sector, very labor intensive
        indirect=22.6,
        induced=14.2,
        type_1=141.0,
        type_2=155.2,
        female_share=0.72,
        youth_share=0.28,
        informal_share=0.34
    ),
    'automotive': SectorMultipliers(
        direct=22.4,       # Growing sector (Renault, etc.)
        indirect=24.8,
        induced=16.2,
        type_1=47.2,
        type_2=63.4,
        female_share=0.18,
        youth_share=0.16,
        informal_share=0.12
    ),
    'food_processing': SectorMultipliers(
        direct=62.8,       # Olive oil, dates, etc.
        indirect=28.4,
        induced=16.4,
        type_1=91.2,
        type_2=107.6,
        female_share=0.38,
        youth_share=0.24,
        informal_share=0.36
    ),
    'chemicals': SectorMultipliers(
        direct=18.4,
        indirect=10.2,
        induced=11.8,
        type_1=28.6,
        type_2=40.4,
        female_share=0.22,
        youth_share=0.16,
        informal_share=0.14
    ),
    'construction': SectorMultipliers(
        direct=78.6,
        indirect=18.4,
        induced=14.2,
        type_1=97.0,
        type_2=111.2,
        female_share=0.04,
        youth_share=0.28,
        informal_share=0.58
    ),
    'utilities': SectorMultipliers(
        direct=9.4,
        indirect=4.2,
        induced=6.8,
        type_1=13.6,
        type_2=20.4,
        female_share=0.18,
        youth_share=0.12,
        informal_share=0.06
    ),
    'trade': SectorMultipliers(
        direct=86.4,
        indirect=10.8,
        induced=14.2,
        type_1=97.2,
        type_2=111.4,
        female_share=0.32,
        youth_share=0.34,
        informal_share=0.64
    ),
    'transport': SectorMultipliers(
        direct=48.2,
        indirect=12.4,
        induced=13.8,
        type_1=60.6,
        type_2=74.4,
        female_share=0.12,
        youth_share=0.22,
        informal_share=0.42
    ),
    'finance': SectorMultipliers(
        direct=28.4,
        indirect=6.8,
        induced=14.2,
        type_1=35.2,
        type_2=49.4,
        female_share=0.46,
        youth_share=0.18,
        informal_share=0.08
    ),
    'public_services': SectorMultipliers(
        direct=64.2,
        indirect=5.4,
        induced=12.4,
        type_1=69.6,
        type_2=82.0,
        female_share=0.52,
        youth_share=0.14,
        informal_share=0.06
    ),
    'other_services': SectorMultipliers(
        direct=82.6,       # Tourism important
        indirect=16.8,
        induced=14.8,
        type_1=99.4,
        type_2=114.2,
        female_share=0.44,
        youth_share=0.36,
        informal_share=0.52
    ),
}


# Viet Nam TiVA-based multipliers (2020 reference year)
# Source: OECD ICIO 2023, aggregated from 45 industries to 14 sectors
# Demographic shares from GSO Viet Nam Labour Force Survey
VIETNAM_TIVA = {
    'agriculture': SectorMultipliers(
        direct=186.0,      # Very high labor intensity, smallholder farming
        indirect=22.4,
        induced=24.8,
        type_1=208.4,
        type_2=233.2,
        female_share=0.50,
        youth_share=0.16,
        informal_share=0.78
    ),
    'mining': SectorMultipliers(
        direct=10.4,        # Capital intensive (coal, oil, gas)
        indirect=6.8,
        induced=8.2,
        type_1=17.2,
        type_2=25.4,
        female_share=0.10,
        youth_share=0.10,
        informal_share=0.18
    ),
    'manufacturing': SectorMultipliers(
        direct=62.4,        # Electronics assembly, high labor use
        indirect=28.6,      # Strong backward linkages
        induced=22.4,
        type_1=91.0,
        type_2=113.4,
        female_share=0.42,
        youth_share=0.22,
        informal_share=0.32
    ),
    'textiles': SectorMultipliers(
        direct=134.2,       # Major export sector, very labor intensive
        indirect=26.8,      # Raw materials linkages
        induced=18.6,
        type_1=161.0,
        type_2=179.6,
        female_share=0.76,
        youth_share=0.28,
        informal_share=0.42
    ),
    'automotive': SectorMultipliers(
        direct=24.6,        # Growing assembly sector
        indirect=22.4,
        induced=16.8,
        type_1=47.0,
        type_2=63.8,
        female_share=0.18,
        youth_share=0.14,
        informal_share=0.14
    ),
    'food_processing': SectorMultipliers(
        direct=72.8,        # Seafood, rice processing
        indirect=34.2,      # Strong agriculture linkages
        induced=20.4,
        type_1=107.0,
        type_2=127.4,
        female_share=0.52,
        youth_share=0.20,
        informal_share=0.38
    ),
    'chemicals': SectorMultipliers(
        direct=18.2,        # Fertilizers, petrochemicals
        indirect=12.8,
        induced=12.4,
        type_1=31.0,
        type_2=43.4,
        female_share=0.28,
        youth_share=0.14,
        informal_share=0.16
    ),
    'construction': SectorMultipliers(
        direct=82.4,        # Rapid urbanization driving construction
        indirect=24.8,
        induced=18.2,
        type_1=107.2,
        type_2=125.4,
        female_share=0.06,
        youth_share=0.22,
        informal_share=0.62
    ),
    'utilities': SectorMultipliers(
        direct=7.8,
        indirect=4.2,
        induced=7.4,
        type_1=12.0,
        type_2=19.4,
        female_share=0.20,
        youth_share=0.10,
        informal_share=0.06
    ),
    'trade': SectorMultipliers(
        direct=92.6,        # Large retail/wholesale workforce
        indirect=14.8,
        induced=18.4,
        type_1=107.4,
        type_2=125.8,
        female_share=0.52,
        youth_share=0.26,
        informal_share=0.68
    ),
    'transport': SectorMultipliers(
        direct=48.4,
        indirect=16.2,
        induced=16.8,
        type_1=64.6,
        type_2=81.4,
        female_share=0.12,
        youth_share=0.18,
        informal_share=0.48
    ),
    'finance': SectorMultipliers(
        direct=18.6,
        indirect=6.4,
        induced=14.2,
        type_1=25.0,
        type_2=39.2,
        female_share=0.48,
        youth_share=0.12,
        informal_share=0.08
    ),
    'public_services': SectorMultipliers(
        direct=52.8,        # Government, health, education
        indirect=5.8,
        induced=12.6,
        type_1=58.6,
        type_2=71.2,
        female_share=0.56,
        youth_share=0.10,
        informal_share=0.06
    ),
    'other_services': SectorMultipliers(
        direct=88.4,        # Tourism, hospitality, personal services
        indirect=16.4,
        induced=17.2,
        type_1=104.8,
        type_2=122.0,
        female_share=0.50,
        youth_share=0.30,
        informal_share=0.56
    ),
}


# Thailand TiVA-based multipliers (2020 reference year)
# Source: OECD ICIO 2023, aggregated from 45 industries to 14 sectors
# Demographic shares from NSO Thailand Labour Force Survey
THAILAND_TIVA = {
    'agriculture': SectorMultipliers(
        direct=148.0,       # Smallholder rice farming, high labor intensity
        indirect=20.8,
        induced=22.4,
        type_1=168.8,
        type_2=191.2,
        female_share=0.42,
        youth_share=0.14,
        informal_share=0.72
    ),
    'mining': SectorMultipliers(
        direct=8.6,         # Natural gas, tin
        indirect=6.2,
        induced=7.8,
        type_1=14.8,
        type_2=22.6,
        female_share=0.08,
        youth_share=0.08,
        informal_share=0.16
    ),
    'manufacturing': SectorMultipliers(
        direct=44.2,        # Electronics, hard disk drives
        indirect=24.8,      # Strong backward linkages
        induced=20.6,
        type_1=69.0,
        type_2=89.6,
        female_share=0.38,
        youth_share=0.18,
        informal_share=0.22
    ),
    'textiles': SectorMultipliers(
        direct=88.6,        # Garments, labor intensive
        indirect=22.4,
        induced=16.2,
        type_1=111.0,
        type_2=127.2,
        female_share=0.72,
        youth_share=0.22,
        informal_share=0.34
    ),
    'automotive': SectorMultipliers(
        direct=16.8,        # ASEAN's largest auto producer
        indirect=26.4,      # Strong supply chain linkages
        induced=19.2,
        type_1=43.2,
        type_2=62.4,
        female_share=0.16,
        youth_share=0.12,
        informal_share=0.08
    ),
    'food_processing': SectorMultipliers(
        direct=58.4,        # Major food exporter (rice, seafood, canned goods)
        indirect=32.6,      # Strong agriculture linkages
        induced=18.8,
        type_1=91.0,
        type_2=109.8,
        female_share=0.46,
        youth_share=0.18,
        informal_share=0.34
    ),
    'chemicals': SectorMultipliers(
        direct=14.6,        # Petrochemicals, rubber
        indirect=11.4,
        induced=12.8,
        type_1=26.0,
        type_2=38.8,
        female_share=0.30,
        youth_share=0.12,
        informal_share=0.12
    ),
    'construction': SectorMultipliers(
        direct=72.4,
        indirect=22.8,
        induced=16.4,
        type_1=95.2,
        type_2=111.6,
        female_share=0.08,
        youth_share=0.24,
        informal_share=0.54
    ),
    'utilities': SectorMultipliers(
        direct=6.8,
        indirect=4.4,
        induced=7.2,
        type_1=11.2,
        type_2=18.4,
        female_share=0.22,
        youth_share=0.08,
        informal_share=0.04
    ),
    'trade': SectorMultipliers(
        direct=84.2,        # Large retail/wholesale sector
        indirect=12.6,
        induced=16.8,
        type_1=96.8,
        type_2=113.6,
        female_share=0.54,
        youth_share=0.24,
        informal_share=0.58
    ),
    'transport': SectorMultipliers(
        direct=42.8,        # Logistics, tourism-related transport
        indirect=14.6,
        induced=15.2,
        type_1=57.4,
        type_2=72.6,
        female_share=0.14,
        youth_share=0.16,
        informal_share=0.38
    ),
    'finance': SectorMultipliers(
        direct=16.4,
        indirect=7.2,
        induced=15.8,       # Higher wages -> higher induced
        type_1=23.6,
        type_2=39.4,
        female_share=0.52,
        youth_share=0.10,
        informal_share=0.06
    ),
    'public_services': SectorMultipliers(
        direct=48.6,
        indirect=5.6,
        induced=13.4,
        type_1=54.2,
        type_2=67.6,
        female_share=0.54,
        youth_share=0.08,
        informal_share=0.04
    ),
    'other_services': SectorMultipliers(
        direct=78.2,        # Tourism (~12% GDP), hospitality, personal services
        indirect=14.8,
        induced=16.4,
        type_1=93.0,
        type_2=109.4,
        female_share=0.52,
        youth_share=0.28,
        informal_share=0.48
    ),
}


# Mozambique: Stylized estimates (not in OECD ICIO)
# Based on World Bank WDI 2024, ILO labor statistics, and regional patterns
# Reference: Low-income economy with high agriculture dependence (69.5% employment)
# and very high informality (95% of employment)
MOZAMBIQUE_STYLIZED = {
    'agriculture': SectorMultipliers(
        direct=168.0,      # Very high labor intensity, 69.5% employment share
        indirect=12.4,     # Limited backward linkages, weak value chains
        induced=14.8,      # Very low wages -> low induced effect
        type_1=180.4,
        type_2=195.2,
        female_share=0.48,  # Significant female participation in subsistence farming
        youth_share=0.24,   # High youth employment in agriculture
        informal_share=0.88  # Extremely high informality in agriculture
    ),
    'mining': SectorMultipliers(
        direct=8.4,        # Extractives: coal, natural gas - very capital intensive
        indirect=6.2,      # Limited local linkages, mostly foreign equipment
        induced=7.8,       # Higher wages but small workforce
        type_1=14.6,
        type_2=22.4,
        female_share=0.06,  # Very low female participation in mining
        youth_share=0.08,   # Low youth employment
        informal_share=0.24  # Some artisanal mining
    ),
    'manufacturing': SectorMultipliers(
        direct=54.8,       # Low industrial base (14.5% GDP), mostly SMEs
        indirect=14.2,     # Weak supply chains, many imports
        induced=12.6,
        type_1=69.0,
        type_2=81.6,
        female_share=0.38,  # Moderate female participation, food processing
        youth_share=0.26,   # Youth in small-scale manufacturing
        informal_share=0.74  # Very high informality
    ),
    'textiles': SectorMultipliers(
        direct=124.0,      # Labor intensive but small sector
        indirect=18.4,     # Limited textile supply chain
        induced=11.8,
        type_1=142.4,
        type_2=154.2,
        female_share=0.76,  # Predominantly female workforce
        youth_share=0.32,   # High youth employment
        informal_share=0.68  # High informality, many small workshops
    ),
    'automotive': SectorMultipliers(
        direct=14.2,       # Very limited automotive sector
        indirect=11.8,     # Mostly assembly/repair, imported parts
        induced=9.4,
        type_1=26.0,
        type_2=35.4,
        female_share=0.08,
        youth_share=0.16,
        informal_share=0.52  # Many informal repair shops
    ),
    'food_processing': SectorMultipliers(
        direct=72.4,       # Important agro-processing: cashews, sugar, seafood
        indirect=32.6,     # Strong agricultural linkages
        induced=14.2,
        type_1=105.0,
        type_2=119.2,
        female_share=0.52,  # High female participation in food processing
        youth_share=0.28,
        informal_share=0.64  # Many informal processors
    ),
    'chemicals': SectorMultipliers(
        direct=12.6,       # Small sector, mostly imports
        indirect=8.4,
        induced=8.2,
        type_1=21.0,
        type_2=29.2,
        female_share=0.18,
        youth_share=0.12,
        informal_share=0.22
    ),
    'construction': SectorMultipliers(
        direct=84.2,       # Labor intensive, LNG infrastructure boom
        indirect=16.8,     # Some local materials, many imports
        induced=12.4,
        type_1=101.0,
        type_2=113.4,
        female_share=0.06,  # Very low female participation
        youth_share=0.34,   # High youth employment in construction
        informal_share=0.78  # Very high informality
    ),
    'utilities': SectorMultipliers(
        direct=7.2,        # Capital intensive, HCB hydropower, limited access
        indirect=3.8,
        induced=6.4,
        type_1=11.0,
        type_2=17.4,
        female_share=0.14,
        youth_share=0.08,
        informal_share=0.08
    ),
    'trade': SectorMultipliers(
        direct=94.6,       # Services 54.7% GDP, trade dominates
        indirect=8.4,      # Limited backward linkages
        induced=11.8,
        type_1=103.0,
        type_2=114.8,
        female_share=0.54,  # High female participation in informal trade
        youth_share=0.38,   # Very high youth in trade
        informal_share=0.92  # Extremely high informality
    ),
    'transport': SectorMultipliers(
        direct=52.4,       # Port corridors, logistics for mining
        indirect=12.2,
        induced=11.4,
        type_1=64.6,
        type_2=76.0,
        female_share=0.12,
        youth_share=0.22,
        informal_share=0.68  # Many informal transport operators
    ),
    'finance': SectorMultipliers(
        direct=18.6,       # Limited financial sector penetration
        indirect=6.4,
        induced=12.8,      # Higher wages in formal finance
        type_1=25.0,
        type_2=37.8,
        female_share=0.42,
        youth_share=0.16,
        informal_share=0.24  # Some informal financial services
    ),
    'public_services': SectorMultipliers(
        direct=68.4,       # Government, health, education - major employer
        indirect=5.2,      # Limited backward linkages
        induced=11.6,
        type_1=73.6,
        type_2=85.2,
        female_share=0.52,  # Moderate-high female in public sector
        youth_share=0.14,
        informal_share=0.12  # Low informality in public sector
    ),
    'other_services': SectorMultipliers(
        direct=86.2,       # Tourism potential (beaches), personal services
        indirect=11.8,
        induced=12.4,
        type_1=98.0,
        type_2=110.4,
        female_share=0.58,  # High female in services
        youth_share=0.36,   # Very high youth employment
        informal_share=0.84  # Very high informality
    ),
}


# Sector-specific import price elasticities of demand.
# Sources: Kee, Nicita & Olarreaga (2008); Fontagné et al. (2022); IMF WEO estimates.
# Negative values: a 1% tariff increase reduces imports by this percentage.
SECTOR_IMPORT_ELASTICITIES: Dict[str, float] = {
    'agriculture': -0.5,        # Food staples: relatively inelastic, limited substitutes
    'mining': -0.6,             # Extractives: inelastic, site-specific commodities
    'manufacturing': -1.5,      # Industrial goods: moderate elasticity, global supply chains
    'textiles': -2.0,           # Highly elastic: many low-cost global producers
    'automotive': -1.8,         # Elastic: deep global value chains, brand competition
    'food_processing': -0.8,    # Moderate: some consumer preference for local brands
    'chemicals': -1.3,          # Moderate: differentiated but substitutable products
    'construction': -0.7,       # Inelastic: local labour dominates, materials less tradeable
    'utilities': -0.4,          # Very inelastic: natural monopoly, regulated pricing
    'trade': -1.0,              # Unit elastic (services, limited import exposure)
    'transport': -0.8,          # Moderate: some substitution between local/foreign carriers
    'finance': -0.5,            # Inelastic: regulatory and trust barriers to switching
    'public_services': -0.3,    # Very inelastic: predominantly domestic provision
    'other_services': -0.6,     # Moderately inelastic: tourism competes with domestic leisure
}


def get_multipliers(country_code: str) -> Dict[str, SectorMultipliers]:
    """
    Get employment multipliers for a country.

    Returns TiVA-based multipliers for ZAF, VNM, THA (OECD ICIO data),
    stylized estimates for TUN, MOZ (not in OECD ICIO).
    """
    code = country_code.upper()
    multiplier_map = {
        'ZAF': SOUTH_AFRICA_TIVA,
        'TUN': TUNISIA_STYLIZED,
        'VNM': VIETNAM_TIVA,
        'THA': THAILAND_TIVA,
        'MOZ': MOZAMBIQUE_STYLIZED,
    }
    return multiplier_map.get(code, TUNISIA_STYLIZED)


def is_tiva_available(country_code: str) -> bool:
    """Check if TiVA data is available for a country."""
    return country_code.upper() in ('ZAF', 'VNM', 'THA')


def get_data_source_info(country_code: str) -> Dict[str, str]:
    """Get information about data sources for a country."""
    code = country_code.upper()
    if code == 'ZAF':
        return {
            'multiplier_source': 'OECD TiVA/ICIO 2023',
            'reference_year': '2020',
            'quality': 'research-grade',
            'notes': 'Employment multipliers derived from OECD Inter-Country Input-Output tables. Demographic shares from Stats SA Labour Force Survey.'
        }
    elif code == 'VNM':
        return {
            'multiplier_source': 'OECD TiVA/ICIO 2023',
            'reference_year': '2020',
            'quality': 'research-grade',
            'notes': 'Employment multipliers derived from OECD Inter-Country Input-Output tables. Demographic shares from GSO Viet Nam Labour Force Survey.'
        }
    elif code == 'THA':
        return {
            'multiplier_source': 'OECD TiVA/ICIO 2023',
            'reference_year': '2020',
            'quality': 'research-grade',
            'notes': 'Employment multipliers derived from OECD Inter-Country Input-Output tables. Demographic shares from NSO Thailand Labour Force Survey.'
        }
    elif code == 'MOZ':
        return {
            'multiplier_source': 'Stylized estimates (World Bank WDI 2024, ILO)',
            'reference_year': '2023-2024',
            'quality': 'illustrative',
            'notes': 'Mozambique is not covered by OECD ICIO. Multipliers are stylized estimates based on World Bank WDI data, ILO labor force statistics, and regional patterns from similar low-income economies. Agriculture employs 69.5% of workforce with 95% informality. Use for educational purposes only.'
        }
    else:
        return {
            'multiplier_source': 'Stylized estimates',
            'reference_year': 'N/A',
            'quality': 'illustrative',
            'notes': 'Country not covered by OECD ICIO. Multipliers are stylized estimates based on regional patterns and ILO statistics. Use for educational purposes only.'
        }
