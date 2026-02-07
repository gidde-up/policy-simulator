"""
Economic Model for Policy Simulation
=====================================
Uses Input-Output analysis with Leontief inverse matrices to calculate
employment effects of policy changes.

This is a DIDACTIC model - it prioritizes educational clarity over
econometric precision, while maintaining economic plausibility.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import TiVA multipliers
from ..data.tiva_multipliers import get_multipliers, is_tiva_available, get_data_source_info


class TimeHorizon(Enum):
    SHORT = 1   # 1 year - immediate/direct effects
    MEDIUM = 3  # 3 years - adjustment period
    LONG = 5    # 5 years - structural transformation


class Sector(Enum):
    """Aggregated sectors based on ISIC classification"""
    AGRICULTURE = "agriculture"
    MINING = "mining"
    MANUFACTURING = "manufacturing"
    TEXTILES = "textiles"
    AUTOMOTIVE = "automotive"
    FOOD_PROCESSING = "food_processing"
    CHEMICALS = "chemicals"
    CONSTRUCTION = "construction"
    UTILITIES = "utilities"
    TRADE = "trade"
    TRANSPORT = "transport"
    FINANCE = "finance"
    PUBLIC_SERVICES = "public_services"
    OTHER_SERVICES = "other_services"


@dataclass
class EmploymentEffect:
    """Employment impact from a policy change"""
    direct_jobs: float
    indirect_jobs: float
    induced_jobs: float
    total_jobs: float

    # Disaggregation
    male_share: float
    female_share: float
    youth_share: float  # 15-24 age group
    adult_share: float

    # Job quality
    formal_share: float
    informal_share: float
    avg_wage_effect: float  # % change

    # Uncertainty
    confidence_low: float
    confidence_high: float


@dataclass
class SectorEffect:
    """Effect on a specific sector"""
    sector: str
    output_change: float  # % change in output
    employment_effect: EmploymentEffect
    value_added_change: float


@dataclass
class PolicyCosts:
    """
    Fiscal and economic costs of a policy intervention.

    All costs are ANNUAL figures (per year), not cumulative over the time horizon.
    Employment figures are cumulative over the time horizon, so cost-per-job
    represents annual cost per job-year equivalent.

    Distinguishes between:
    - Fiscal cost: Direct government budget impact (spending or revenue)
    - Economic cost: Total welfare cost including deadweight loss
    """
    # Fiscal impacts (in millions USD, per year)
    tariff_revenue_gross: float = 0.0      # Annual revenue before import reduction
    tariff_revenue_net: float = 0.0        # Annual revenue after behavioral response
    subsidy_cost: float = 0.0              # Annual subsidy spending
    sme_stimulus_cost: float = 0.0         # Annual SME program spending
    productivity_cost: float = 0.0         # Annual productivity investment spending

    # Net fiscal impact (positive = revenue, negative = cost), per year
    net_fiscal_impact: float = 0.0

    # Economic costs (deadweight loss, efficiency costs), per year
    tariff_deadweight_loss: float = 0.0    # Annual consumer/producer surplus loss
    tariff_trade_reduction: float = 0.0    # Annual value of foregone imports
    efficiency_cost: float = 0.0           # Annual admin costs, market distortions

    # Total economic cost (always positive or zero), per year
    total_economic_cost: float = 0.0

    # Per-job metrics (annual cost per job-year)
    cost_per_job_fiscal: float = 0.0       # Annual fiscal cost per job
    cost_per_job_economic: float = 0.0     # Annual economic cost per job

    # Breakdown by policy type
    cost_breakdown: Dict[str, float] = None

    def __post_init__(self):
        if self.cost_breakdown is None:
            self.cost_breakdown = {}


@dataclass
class PolicyScenario:
    """A complete policy scenario with multiple levers"""
    name: str
    tariff_changes: Dict[str, float]  # sector -> % change
    subsidy_changes: Dict[str, float]
    sme_stimulus: float  # % of GDP
    productivity_investment: float  # % increase target
    time_horizon: TimeHorizon


class InputOutputModel:
    """
    Leontief Input-Output Model for Employment Simulation

    The model uses:
    - Technical coefficients matrix (A): inter-industry requirements
    - Leontief inverse (L): total requirements matrix = (I - A)^(-1)
    - Employment coefficients (e): jobs per unit of output

    Employment multiplier = e * L * final_demand_change
    """

    def __init__(self, country_code: str):
        self.country_code = country_code
        self.sectors = list(Sector)
        self.n_sectors = len(self.sectors)

        # Country GDP in millions USD (2023 approximate values)
        self.gdp_millions = {'ZAF': 400000, 'TUN': 50000}.get(country_code, 100000)

        # Sector shares of GDP
        self.sector_shares = self._get_sector_shares()

        # Check if TiVA data is available for this country
        self.use_tiva = is_tiva_available(country_code)
        self.data_source_info = get_data_source_info(country_code)

        # Load TiVA multipliers (available for ZAF, stylized for TUN)
        self.tiva_multipliers = get_multipliers(country_code)

        # Load country-specific I-O data
        self._load_io_tables()
        self._load_employment_coefficients()
        self._load_demographic_shares()

    def _get_sector_shares(self) -> Dict[str, float]:
        """Sector shares of GDP"""
        if self.country_code == "ZAF":
            return {'agriculture': 0.025, 'mining': 0.08, 'manufacturing': 0.12,
                    'textiles': 0.008, 'automotive': 0.045, 'food_processing': 0.025,
                    'chemicals': 0.035, 'construction': 0.035, 'utilities': 0.025,
                    'trade': 0.15, 'transport': 0.09, 'finance': 0.21,
                    'public_services': 0.06, 'other_services': 0.04}
        else:
            return {'agriculture': 0.10, 'mining': 0.02, 'manufacturing': 0.12,
                    'textiles': 0.06, 'automotive': 0.03, 'food_processing': 0.05,
                    'chemicals': 0.04, 'construction': 0.05, 'utilities': 0.02,
                    'trade': 0.12, 'transport': 0.07, 'finance': 0.06,
                    'public_services': 0.12, 'other_services': 0.04}

    def _load_io_tables(self):
        """
        Load Input-Output tables for the country.

        In production, these would come from OECD ICIO database.
        Here we use stylized matrices based on typical developing country structures.
        """
        # Technical coefficients matrix A (simplified)
        # Each row i shows how much input from sector i is needed per unit output of sector j

        if self.country_code == "ZAF":
            self._load_south_africa_io()
        elif self.country_code == "TUN":
            self._load_tunisia_io()
        else:
            self._load_default_io()

        # Calculate Leontief inverse: L = (I - A)^(-1)
        I = np.eye(self.n_sectors)
        self.leontief_inverse = np.linalg.inv(I - self.tech_coefficients)

        # Type II multiplier includes induced consumption effects
        # Approximated by scaling factor (typically 1.3-1.6 in developing countries)
        self.induced_multiplier = 1.4

    def _load_south_africa_io(self):
        """
        South Africa stylized I-O coefficients
        Based on Stats SA Supply-Use Tables structure
        """
        n = self.n_sectors

        # Initialize with small baseline inter-industry flows
        self.tech_coefficients = np.random.uniform(0.01, 0.05, (n, n))

        # Set key inter-industry linkages for South Africa
        sector_idx = {s.value: i for i, s in enumerate(self.sectors)}

        # Mining feeds into manufacturing
        self.tech_coefficients[sector_idx['mining'], sector_idx['manufacturing']] = 0.15
        self.tech_coefficients[sector_idx['mining'], sector_idx['chemicals']] = 0.12

        # Agriculture feeds food processing
        self.tech_coefficients[sector_idx['agriculture'], sector_idx['food_processing']] = 0.25

        # Manufacturing supplies automotive
        self.tech_coefficients[sector_idx['manufacturing'], sector_idx['automotive']] = 0.30
        self.tech_coefficients[sector_idx['chemicals'], sector_idx['automotive']] = 0.08

        # Construction uses various inputs
        self.tech_coefficients[sector_idx['manufacturing'], sector_idx['construction']] = 0.18
        self.tech_coefficients[sector_idx['mining'], sector_idx['construction']] = 0.10

        # Services are relatively less connected to goods sectors
        for svc in ['trade', 'transport', 'finance', 'public_services', 'other_services']:
            for goods in ['manufacturing', 'automotive', 'construction']:
                self.tech_coefficients[sector_idx[svc], sector_idx[goods]] = 0.03

        # Ensure matrix is productive (row sums < 1)
        row_sums = self.tech_coefficients.sum(axis=0)
        for j in range(n):
            if row_sums[j] >= 0.9:
                self.tech_coefficients[:, j] *= 0.8 / row_sums[j]

    def _load_tunisia_io(self):
        """
        Tunisia stylized I-O coefficients
        Based on INS Tunisia national accounts structure
        """
        n = self.n_sectors

        self.tech_coefficients = np.random.uniform(0.01, 0.04, (n, n))

        sector_idx = {s.value: i for i, s in enumerate(self.sectors)}

        # Tunisia's economy: textiles, tourism, agriculture, phosphates

        # Agriculture and food processing linkage
        self.tech_coefficients[sector_idx['agriculture'], sector_idx['food_processing']] = 0.28

        # Textiles sector (important export)
        self.tech_coefficients[sector_idx['textiles'], sector_idx['trade']] = 0.08
        self.tech_coefficients[sector_idx['chemicals'], sector_idx['textiles']] = 0.10

        # Mining (phosphates) feeds chemicals
        self.tech_coefficients[sector_idx['mining'], sector_idx['chemicals']] = 0.20

        # Services (tourism-related)
        self.tech_coefficients[sector_idx['food_processing'], sector_idx['other_services']] = 0.06
        self.tech_coefficients[sector_idx['transport'], sector_idx['other_services']] = 0.08

        # Manufacturing sector
        self.tech_coefficients[sector_idx['manufacturing'], sector_idx['automotive']] = 0.22

        # Ensure productivity
        row_sums = self.tech_coefficients.sum(axis=0)
        for j in range(n):
            if row_sums[j] >= 0.9:
                self.tech_coefficients[:, j] *= 0.8 / row_sums[j]

    def _load_default_io(self):
        """Default generic developing country I-O structure"""
        n = self.n_sectors
        self.tech_coefficients = np.random.uniform(0.02, 0.06, (n, n))

        row_sums = self.tech_coefficients.sum(axis=0)
        for j in range(n):
            if row_sums[j] >= 0.9:
                self.tech_coefficients[:, j] *= 0.8 / row_sums[j]

    def _load_employment_coefficients(self):
        """
        Employment coefficients: jobs per million USD of output

        Now uses TiVA-based multipliers for South Africa (OECD data),
        stylized estimates for Tunisia.
        """
        # Use direct employment coefficients from TiVA data
        self.employment_coefficients = np.array([
            self.tiva_multipliers[s.value].direct
            for s in self.sectors
        ])

    def _load_demographic_shares(self):
        """
        Demographic employment shares by sector.

        Now uses TiVA-based shares for South Africa (from Stats SA Labour Force Survey),
        stylized estimates for Tunisia (from ILO statistics).
        """
        # Load from TiVA multiplier data
        self.female_shares = {
            s.value: self.tiva_multipliers[s.value].female_share
            for s in self.sectors
        }

        self.youth_shares = {
            s.value: self.tiva_multipliers[s.value].youth_share
            for s in self.sectors
        }

        self.informal_shares = {
            s.value: self.tiva_multipliers[s.value].informal_share
            for s in self.sectors
        }

    def calculate_employment_multipliers(self) -> Dict[str, Dict[str, float]]:
        """
        Return employment multipliers for each sector.

        For South Africa: Uses OECD TiVA-based multipliers (research-grade).
        For Tunisia: Uses stylized estimates (illustrative only).

        Type I = Direct + Indirect effects
        Type II = Direct + Indirect + Induced effects
        """
        multipliers = {}

        for sector in self.sectors:
            tiva = self.tiva_multipliers[sector.value]
            multipliers[sector.value] = {
                'direct': tiva.direct,
                'indirect': tiva.indirect,
                'induced': tiva.induced,
                'type_1': tiva.type_1,
                'type_2': tiva.type_2
            }

        return multipliers

    def simulate_policy(self, scenario: PolicyScenario) -> Dict:
        """
        Simulate employment effects of a policy scenario.

        Returns detailed breakdown of job creation by sector,
        demographics, and job quality.
        """
        results = {
            'scenario_name': scenario.name,
            'country': self.country_code,
            'time_horizon': scenario.time_horizon.value,
            'sector_effects': [],
            'aggregate': None,
            'transmission_paths': []
        }

        # Calculate demand shocks from policies
        demand_changes = self._calculate_demand_shocks(scenario)

        # Get employment multipliers
        multipliers = self.calculate_employment_multipliers()

        # Calculate sector-by-sector effects
        total_direct = 0
        total_indirect = 0
        total_induced = 0

        weighted_female = 0
        weighted_youth = 0
        weighted_informal = 0
        total_jobs = 0

        for i, sector in enumerate(self.sectors):
            sector_name = sector.value
            demand_change = demand_changes.get(sector_name, 0)

            if abs(demand_change) < 0.001:
                continue

            mult = multipliers[sector_name]

            # Scale by time horizon (effects build up over time)
            time_scale = self._get_time_scale(scenario.time_horizon)

            # Calculate job effects
            direct = demand_change * mult['direct'] * time_scale['direct']
            indirect = demand_change * mult['indirect'] * time_scale['indirect']
            induced = demand_change * mult['induced'] * time_scale['induced']
            total = direct + indirect + induced

            # Demographic breakdown
            female_share = self.female_shares[sector_name]
            youth_share = self.youth_shares[sector_name]
            informal_share = self.informal_shares[sector_name]

            # Add uncertainty (±15-25% depending on sector)
            uncertainty = 0.20 if sector_name in ['agriculture', 'other_services'] else 0.15

            effect = EmploymentEffect(
                direct_jobs=direct,
                indirect_jobs=indirect,
                induced_jobs=induced,
                total_jobs=total,
                male_share=1 - female_share,
                female_share=female_share,
                youth_share=youth_share,
                adult_share=1 - youth_share,
                formal_share=1 - informal_share,
                informal_share=informal_share,
                avg_wage_effect=self._estimate_wage_effect(scenario, sector_name),
                confidence_low=total * (1 - uncertainty),
                confidence_high=total * (1 + uncertainty)
            )

            sector_effect = SectorEffect(
                sector=sector_name,
                output_change=demand_change,
                employment_effect=effect,
                value_added_change=demand_change * 0.4  # Approximate VA/output ratio
            )

            results['sector_effects'].append(sector_effect)

            # Accumulate totals
            total_direct += direct
            total_indirect += indirect
            total_induced += induced

            if total > 0:
                weighted_female += female_share * total
                weighted_youth += youth_share * total
                weighted_informal += informal_share * total
                total_jobs += total

        # Calculate aggregate effect
        if total_jobs > 0:
            agg_female = weighted_female / total_jobs
            agg_youth = weighted_youth / total_jobs
            agg_informal = weighted_informal / total_jobs
        else:
            agg_female = agg_youth = agg_informal = 0

        total_all = total_direct + total_indirect + total_induced

        results['aggregate'] = EmploymentEffect(
            direct_jobs=total_direct,
            indirect_jobs=total_indirect,
            induced_jobs=total_induced,
            total_jobs=total_all,
            male_share=1 - agg_female,
            female_share=agg_female,
            youth_share=agg_youth,
            adult_share=1 - agg_youth,
            formal_share=1 - agg_informal,
            informal_share=agg_informal,
            avg_wage_effect=self._estimate_aggregate_wage_effect(scenario),
            confidence_low=total_all * 0.80,
            confidence_high=total_all * 1.20
        )

        # Build transmission paths for Sankey diagram
        results['transmission_paths'] = self._build_transmission_paths(
            scenario, demand_changes, multipliers
        )

        # Calculate policy costs
        results['costs'] = self._calculate_policy_costs(scenario, total_all)

        return results

    def _calculate_policy_costs(self, scenario: PolicyScenario, total_jobs: float) -> PolicyCosts:
        """
        Calculate fiscal and economic costs of the policy intervention.

        All costs are calculated as ANNUAL flows (per year), not cumulative.
        Cost-per-job represents annual fiscal/economic cost per job-year.

        Key economic insights:
        - Tariffs generate revenue BUT reduce imports (Laffer curve effect)
        - Tariffs create deadweight loss (consumer surplus loss > producer gain + revenue)
        - Subsidies are pure fiscal cost
        - SME stimulus has fiscal cost but some tax revenue returns
        - Cost per job should account for ALL costs, not just fiscal
        """
        costs = PolicyCosts()

        # ===== TARIFF COSTS/REVENUES =====
        # Import value estimates by sector (as % of sector GDP, stylized)
        import_shares = {
            'agriculture': 0.15, 'mining': 0.10, 'manufacturing': 0.35,
            'textiles': 0.40, 'automotive': 0.45, 'food_processing': 0.20,
            'chemicals': 0.35, 'construction': 0.15, 'utilities': 0.10,
            'trade': 0.25, 'transport': 0.20, 'finance': 0.10,
            'public_services': 0.05, 'other_services': 0.15,
        }

        # Import demand elasticity (how much imports fall when price rises)
        # Typical range: -0.5 to -2.0; we use -1.2 as middle estimate
        import_elasticity = -1.2

        for sector, tariff_pct in scenario.tariff_changes.items():
            if tariff_pct <= 0:
                continue

            sector_gdp = self.gdp_millions * self.sector_shares.get(sector, 0.05)
            import_value = sector_gdp * import_shares.get(sector, 0.20)

            # Gross revenue (naive: tariff × imports)
            gross_revenue = import_value * (tariff_pct / 100)

            # Import reduction due to tariff (behavioral response)
            # Higher prices → fewer imports
            # % change in imports = elasticity × % change in price
            import_reduction_pct = import_elasticity * (tariff_pct / 100)
            remaining_imports = import_value * (1 + import_reduction_pct)
            remaining_imports = max(0, remaining_imports)  # Can't go negative

            # Net revenue after behavioral response
            net_revenue = remaining_imports * (tariff_pct / 100)

            # Deadweight loss (Harberger triangle)
            # DWL = 0.5 × tariff² × elasticity × import_value
            # This represents efficiency loss from market distortion
            dwl = 0.5 * (tariff_pct / 100) ** 2 * abs(import_elasticity) * import_value

            # Foregone trade value
            trade_reduction = import_value - remaining_imports

            costs.tariff_revenue_gross += gross_revenue
            costs.tariff_revenue_net += net_revenue
            costs.tariff_deadweight_loss += dwl
            costs.tariff_trade_reduction += trade_reduction

        # ===== SUBSIDY COSTS =====
        for sector, subsidy_pct in scenario.subsidy_changes.items():
            if subsidy_pct <= 0:
                continue

            sector_gdp = self.gdp_millions * self.sector_shares.get(sector, 0.05)
            # Subsidy cost = subsidy rate × sector output
            # Assume subsidy applies to ~50% of sector (targeted firms)
            subsidy_cost = sector_gdp * (subsidy_pct / 100) * 0.5
            costs.subsidy_cost += subsidy_cost

        # ===== SME STIMULUS COSTS =====
        if scenario.sme_stimulus > 0:
            costs.sme_stimulus_cost = self.gdp_millions * (scenario.sme_stimulus / 100)

        # ===== PRODUCTIVITY INVESTMENT COSTS =====
        if scenario.productivity_investment > 0:
            # Productivity investment as direct government spending
            prod_sectors = ['manufacturing', 'automotive', 'chemicals', 'food_processing']
            for sector in prod_sectors:
                sector_gdp = self.gdp_millions * self.sector_shares.get(sector, 0.05)
                costs.productivity_cost += sector_gdp * (scenario.productivity_investment / 100) * 0.3

        # ===== AGGREGATE CALCULATIONS =====
        # Net fiscal impact (positive = net revenue to government)
        costs.net_fiscal_impact = (
            costs.tariff_revenue_net
            - costs.subsidy_cost
            - costs.sme_stimulus_cost
            - costs.productivity_cost
        )

        # Total economic cost (includes deadweight loss)
        # Even if tariffs generate revenue, there's still an economic cost
        costs.efficiency_cost = costs.tariff_deadweight_loss * 0.2  # Admin/compliance costs

        costs.total_economic_cost = (
            costs.tariff_deadweight_loss
            + costs.efficiency_cost
            + costs.subsidy_cost
            + costs.sme_stimulus_cost
            + costs.productivity_cost
        )

        # Per-job metrics (convert from millions to dollars)
        if total_jobs > 0:
            # Fiscal cost per job (can be negative if tariff revenue exceeds spending)
            # Multiply by 1,000,000 to convert from millions USD to USD
            costs.cost_per_job_fiscal = (-costs.net_fiscal_impact * 1_000_000) / total_jobs
            # Economic cost per job (always positive)
            costs.cost_per_job_economic = (costs.total_economic_cost * 1_000_000) / total_jobs
        elif total_jobs < 0:
            # Job losses - costs are infinite per job "created"
            costs.cost_per_job_fiscal = float('inf')
            costs.cost_per_job_economic = float('inf')

        # Cost breakdown by policy type
        costs.cost_breakdown = {
            'tariffs': {
                'gross_revenue': costs.tariff_revenue_gross,
                'net_revenue': costs.tariff_revenue_net,
                'deadweight_loss': costs.tariff_deadweight_loss,
                'trade_reduction': costs.tariff_trade_reduction,
                'net_fiscal': costs.tariff_revenue_net,
                'net_economic': costs.tariff_deadweight_loss - costs.tariff_revenue_net,
            },
            'subsidies': {
                'fiscal_cost': costs.subsidy_cost,
            },
            'sme_stimulus': {
                'fiscal_cost': costs.sme_stimulus_cost,
            },
            'productivity': {
                'fiscal_cost': costs.productivity_cost,
            },
        }

        return costs

    def _calculate_demand_shocks(self, scenario: PolicyScenario) -> Dict[str, float]:
        """
        Translate policy levers into demand shocks in MILLIONS USD.

        Employment coefficients are jobs per million USD, so demand changes
        must be in millions USD to get realistic job numbers.

        This model includes:
        - Non-linear tariff effects (diminishing returns, negative at extremes)
        - Policy synergy bonuses for balanced policy mixes
        - Diminishing returns on subsidies and stimulus
        - Negative externalities at extreme policy levels
        """
        demand_changes = {}

        # Calculate policy intensity metrics for synergy calculations
        policy_metrics = self._calculate_policy_metrics(scenario)

        # TARIFF effects with non-linear response curve
        tariff_effect = self._calculate_tariff_effects(scenario, policy_metrics)
        for sector, effect in tariff_effect.items():
            demand_changes[sector] = demand_changes.get(sector, 0) + effect

        # SUBSIDY effects with diminishing returns
        subsidy_effect = self._calculate_subsidy_effects(scenario, policy_metrics)
        for sector, effect in subsidy_effect.items():
            demand_changes[sector] = demand_changes.get(sector, 0) + effect

        # SME STIMULUS with diminishing returns and fiscal constraints
        sme_effect = self._calculate_sme_effects(scenario, policy_metrics)
        for sector, effect in sme_effect.items():
            demand_changes[sector] = demand_changes.get(sector, 0) + effect

        # PRODUCTIVITY INVESTMENT effects
        prod_effect = self._calculate_productivity_effects(scenario, policy_metrics)
        for sector, effect in prod_effect.items():
            demand_changes[sector] = demand_changes.get(sector, 0) + effect

        # Apply policy synergy multiplier (balanced mix is more effective)
        synergy_multiplier = self._calculate_synergy_multiplier(scenario, policy_metrics)
        for sector in demand_changes:
            demand_changes[sector] *= synergy_multiplier

        return demand_changes

    def _calculate_policy_metrics(self, scenario: PolicyScenario) -> Dict[str, float]:
        """Calculate aggregate policy intensity metrics for synergy calculations."""
        total_tariff = sum(abs(v) for v in scenario.tariff_changes.values())
        total_subsidy = sum(abs(v) for v in scenario.subsidy_changes.values())
        num_active_tariffs = sum(1 for v in scenario.tariff_changes.values() if abs(v) > 0.5)
        num_active_subsidies = sum(1 for v in scenario.subsidy_changes.values() if abs(v) > 0.5)

        return {
            'total_tariff': total_tariff,
            'total_subsidy': total_subsidy,
            'avg_tariff': total_tariff / max(num_active_tariffs, 1),
            'avg_subsidy': total_subsidy / max(num_active_subsidies, 1),
            'num_active_policies': (
                num_active_tariffs + num_active_subsidies +
                (1 if scenario.sme_stimulus > 0.1 else 0) +
                (1 if scenario.productivity_investment > 0.1 else 0)
            ),
            'has_tariff': num_active_tariffs > 0,
            'has_subsidy': num_active_subsidies > 0,
            'has_sme': scenario.sme_stimulus > 0.1,
            'has_productivity': scenario.productivity_investment > 0.1,
        }

    def _calculate_tariff_effects(
        self, scenario: PolicyScenario, metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate tariff effects with realistic non-linear response.

        Economic theory suggests:
        - Low tariffs (0-10%): Moderate positive effect on domestic production
        - Medium tariffs (10-20%): Diminishing returns, some trade diversion costs
        - High tariffs (>20%): Negative net effects from retaliation, inefficiency,
          higher input costs, and reduced export competitiveness
        """
        effects = {}

        for sector, tariff_pct in scenario.tariff_changes.items():
            if abs(tariff_pct) < 0.1:
                continue

            sector_gdp = self.gdp_millions * self.sector_shares.get(sector, 0.05)

            # Non-linear tariff response function
            # Positive effects peak around 8-12%, turn negative above ~22%
            if tariff_pct >= 0:
                # Positive tariff: protection effect with diminishing returns
                # Uses a modified logistic curve
                optimal_tariff = 10.0  # Optimal tariff level
                steepness = 0.15  # How quickly returns diminish

                # Base elasticity at optimal point
                base_elasticity = 0.35

                # Diminishing returns above optimal
                if tariff_pct <= optimal_tariff:
                    # Linear increase up to optimal
                    effective_elasticity = base_elasticity * (tariff_pct / optimal_tariff)
                else:
                    # Diminishing returns, eventually negative
                    # At 20%: ~0.28 elasticity, at 25%: ~0.15, at 30%: negative
                    excess = tariff_pct - optimal_tariff
                    decay = np.exp(-steepness * excess)
                    # Negative term grows with extreme tariffs (retaliation, inefficiency)
                    negative_effect = 0.02 * (excess ** 1.5) if excess > 10 else 0
                    effective_elasticity = base_elasticity * decay - negative_effect

                # Trade diversion cost: high tariffs hurt export-oriented sectors
                export_penalty = 0
                if tariff_pct > 15:
                    export_sectors = ['automotive', 'textiles', 'manufacturing', 'chemicals']
                    if sector in export_sectors:
                        export_penalty = (tariff_pct - 15) * 0.01 * sector_gdp

                effect = sector_gdp * (tariff_pct / 100) * effective_elasticity - export_penalty

            else:
                # Negative tariff (liberalization): can have positive efficiency effects
                # but also exposes domestic industry to competition
                liberalization_pct = abs(tariff_pct)
                # Small liberalization can improve efficiency
                if liberalization_pct <= 10:
                    effect = -sector_gdp * (liberalization_pct / 100) * 0.2
                else:
                    # Large liberalization hurts domestic industry
                    effect = -sector_gdp * (liberalization_pct / 100) * 0.4

            effects[sector] = effect

        # Cross-sector retaliation effect: aggregate high tariffs trigger partner retaliation
        if metrics['total_tariff'] > 50:
            retaliation_factor = 1 - min(0.3, (metrics['total_tariff'] - 50) * 0.01)
            for sector in effects:
                effects[sector] *= retaliation_factor

        return effects

    def _calculate_subsidy_effects(
        self, scenario: PolicyScenario, metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate subsidy effects with diminishing returns and fiscal constraints.

        Higher subsidies face:
        - Diminishing returns (inefficiency, rent-seeking)
        - Fiscal crowding out effects
        - WTO compliance concerns at extreme levels
        """
        effects = {}

        # Total fiscal cost affects effectiveness (crowding out)
        total_subsidy_cost = metrics['total_subsidy']
        fiscal_constraint = 1.0
        if total_subsidy_cost > 30:  # More than 30% total subsidy commitment
            fiscal_constraint = 1.0 - min(0.4, (total_subsidy_cost - 30) * 0.02)

        for sector, subsidy_pct in scenario.subsidy_changes.items():
            if subsidy_pct < 0.1:
                continue

            sector_gdp = self.gdp_millions * self.sector_shares.get(sector, 0.05)

            # Diminishing returns on subsidies
            # First 5%: high elasticity (0.9), then declining
            if subsidy_pct <= 5:
                effective_elasticity = 0.9
            elif subsidy_pct <= 10:
                effective_elasticity = 0.9 - (subsidy_pct - 5) * 0.06  # 0.9 -> 0.6
            elif subsidy_pct <= 15:
                effective_elasticity = 0.6 - (subsidy_pct - 10) * 0.06  # 0.6 -> 0.3
            else:
                effective_elasticity = max(0.1, 0.3 - (subsidy_pct - 15) * 0.04)

            effect = sector_gdp * (subsidy_pct / 100) * effective_elasticity * fiscal_constraint
            effects[sector] = effect

        return effects

    def _calculate_sme_effects(
        self, scenario: PolicyScenario, metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate SME stimulus effects with diminishing returns.

        SME stimulus is most effective at moderate levels (1-2% GDP).
        Higher levels face absorption constraints and inflation effects.
        """
        effects = {}

        if scenario.sme_stimulus < 0.1:
            return effects

        sme_sectors = ['trade', 'other_services', 'food_processing', 'textiles', 'construction']

        # Fiscal multiplier with diminishing returns
        # 1% GDP: multiplier ~1.5
        # 2% GDP: multiplier ~1.35
        # 3% GDP: multiplier ~1.15
        # 4%+ GDP: multiplier ~1.0 (absorption constraints)
        stimulus_pct = scenario.sme_stimulus
        if stimulus_pct <= 1:
            multiplier = 1.5
        elif stimulus_pct <= 2:
            multiplier = 1.5 - (stimulus_pct - 1) * 0.15
        elif stimulus_pct <= 3:
            multiplier = 1.35 - (stimulus_pct - 2) * 0.2
        else:
            multiplier = max(0.9, 1.15 - (stimulus_pct - 3) * 0.15)

        total_stimulus = self.gdp_millions * (stimulus_pct / 100) * multiplier
        stimulus_per_sector = total_stimulus / len(sme_sectors)

        for sector in sme_sectors:
            effects[sector] = stimulus_per_sector

        return effects

    def _calculate_productivity_effects(
        self, scenario: PolicyScenario, metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate productivity investment effects.

        Productivity investments have delayed effects that grow over time.
        Short-term: may reduce jobs (automation)
        Long-term: creates higher-quality jobs, increases competitiveness
        """
        effects = {}

        if scenario.productivity_investment < 0.1:
            return effects

        prod_sectors = ['manufacturing', 'automotive', 'chemicals', 'food_processing']

        # Time-dependent multiplier
        if scenario.time_horizon == TimeHorizon.SHORT:
            time_mult = 0.2  # Limited short-term effect
            job_quality_bonus = 0  # No quality improvement yet
        elif scenario.time_horizon == TimeHorizon.MEDIUM:
            time_mult = 0.6
            job_quality_bonus = 0.1  # Some quality jobs emerging
        else:  # LONG
            time_mult = 1.0
            job_quality_bonus = 0.2  # Significant quality improvement

        # Diminishing returns on productivity investment
        prod_pct = scenario.productivity_investment
        if prod_pct <= 5:
            effectiveness = 0.5
        else:
            effectiveness = 0.5 - (prod_pct - 5) * 0.03  # Slower diminishing

        for sector in prod_sectors:
            sector_gdp = self.gdp_millions * self.sector_shares.get(sector, 0.05)
            base_effect = sector_gdp * (prod_pct / 100) * effectiveness * time_mult
            # Add bonus for job quality improvement
            quality_effect = base_effect * job_quality_bonus
            effects[sector] = base_effect + quality_effect

        return effects

    def _calculate_synergy_multiplier(
        self, scenario: PolicyScenario, metrics: Dict[str, float]
    ) -> float:
        """
        Calculate policy synergy multiplier.

        A balanced policy mix is more effective than isolated interventions.
        However, too many simultaneous policies can create implementation challenges.

        Optimal: 2-3 complementary policy instruments
        """
        num_policies = metrics['num_active_policies']

        if num_policies == 0:
            return 1.0
        elif num_policies == 1:
            # Single policy: no synergy bonus
            return 1.0
        elif num_policies == 2:
            # Two policies: moderate synergy
            synergy = 1.1
        elif num_policies == 3:
            # Three policies: optimal synergy
            synergy = 1.15
        else:
            # Four policies: implementation complexity reduces effectiveness
            synergy = 1.1

        # Complementarity bonus: certain combinations work better together
        complementarity = 1.0

        # Subsidy + Productivity: complementary (invest in capacity + upgrade it)
        if metrics['has_subsidy'] and metrics['has_productivity']:
            complementarity += 0.05

        # SME + moderate tariffs: complementary (protect small firms + support them)
        if metrics['has_sme'] and metrics['has_tariff'] and metrics['avg_tariff'] <= 15:
            complementarity += 0.05

        # High tariffs + no productivity: non-complementary (protection without upgrading)
        if metrics['has_tariff'] and metrics['avg_tariff'] > 15 and not metrics['has_productivity']:
            complementarity -= 0.1

        # High subsidies + high tariffs: can crowd out, less complementary
        if metrics['has_subsidy'] and metrics['has_tariff']:
            if metrics['avg_subsidy'] > 10 and metrics['avg_tariff'] > 15:
                complementarity -= 0.1

        return synergy * complementarity

    def _get_time_scale(self, horizon: TimeHorizon) -> Dict[str, float]:
        """
        Time scaling factors for different effect types.

        Direct effects materialize quickly, indirect/induced take longer.
        """
        if horizon == TimeHorizon.SHORT:
            return {'direct': 0.7, 'indirect': 0.3, 'induced': 0.2}
        elif horizon == TimeHorizon.MEDIUM:
            return {'direct': 1.0, 'indirect': 0.8, 'induced': 0.6}
        else:  # LONG
            return {'direct': 1.0, 'indirect': 1.0, 'induced': 0.9}

    def _estimate_wage_effect(self, scenario: PolicyScenario, sector: str) -> float:
        """Estimate wage effects from policy (simplified)"""
        # Tariffs can increase wages in protected sectors
        tariff_effect = scenario.tariff_changes.get(sector, 0) * 0.1
        # Subsidies have smaller wage effects
        subsidy_effect = scenario.subsidy_changes.get(sector, 0) * 0.05
        # Productivity investment increases wages in the long run
        prod_effect = scenario.productivity_investment * 0.15 if sector in [
            'manufacturing', 'automotive', 'chemicals'
        ] else 0

        return tariff_effect + subsidy_effect + prod_effect

    def _estimate_aggregate_wage_effect(self, scenario: PolicyScenario) -> float:
        """Aggregate wage effect across all sectors"""
        total_tariff = sum(scenario.tariff_changes.values()) * 0.05
        total_subsidy = sum(scenario.subsidy_changes.values()) * 0.03
        prod_effect = scenario.productivity_investment * 0.10

        return total_tariff + total_subsidy + prod_effect

    def _build_transmission_paths(
        self,
        scenario: PolicyScenario,
        demand_changes: Dict[str, float],
        multipliers: Dict[str, Dict[str, float]]
    ) -> List[Dict]:
        """
        Build transmission paths for Sankey visualization.

        Structure: Policy → Sector → Effect Type → Demographic
        """
        paths = []

        # Group policies
        policies = []
        if scenario.tariff_changes:
            policies.append(('Tariff Policy', 'tariff'))
        if scenario.subsidy_changes:
            policies.append(('Subsidy Policy', 'subsidy'))
        if scenario.sme_stimulus > 0:
            policies.append(('SME Stimulus', 'sme'))
        if scenario.productivity_investment > 0:
            policies.append(('Industrial Policy', 'productivity'))

        for policy_name, policy_type in policies:
            for sector, demand in demand_changes.items():
                if abs(demand) < 1:  # Less than $1M
                    continue

                mult = multipliers[sector]
                time_scale = self._get_time_scale(scenario.time_horizon)

                # Policy → Sector (scale for visualization)
                paths.append({
                    'source': policy_name,
                    'target': sector.replace('_', ' ').title(),
                    'value': abs(demand) / 100,
                    'type': 'policy_to_sector'
                })

                # Sector → Effect types
                direct = demand * mult['direct'] * time_scale['direct']
                indirect = demand * mult['indirect'] * time_scale['indirect']
                induced = demand * mult['induced'] * time_scale['induced']

                if abs(direct) > 100:
                    paths.append({
                        'source': sector.replace('_', ' ').title(),
                        'target': 'Direct Jobs',
                        'value': abs(direct) / 100,
                        'type': 'sector_to_effect'
                    })

                if abs(indirect) > 100:
                    paths.append({
                        'source': sector.replace('_', ' ').title(),
                        'target': 'Indirect Jobs',
                        'value': abs(indirect) / 100,
                        'type': 'sector_to_effect'
                    })

                if abs(induced) > 100:
                    paths.append({
                        'source': sector.replace('_', ' ').title(),
                        'target': 'Induced Jobs',
                        'value': abs(induced) / 100,
                        'type': 'sector_to_effect'
                    })

        # Aggregate effect types → demographics
        total_jobs = sum(
            demand_changes.get(s.value, 0) * multipliers[s.value]['type_2']
            for s in self.sectors
        )

        if abs(total_jobs) > 0:
            # Approximate demographic split
            paths.append({
                'source': 'Direct Jobs',
                'target': 'Female Workers',
                'value': abs(total_jobs * 0.35 * 0.4),
                'type': 'effect_to_demo'
            })
            paths.append({
                'source': 'Direct Jobs',
                'target': 'Male Workers',
                'value': abs(total_jobs * 0.65 * 0.4),
                'type': 'effect_to_demo'
            })
            paths.append({
                'source': 'Indirect Jobs',
                'target': 'Youth (15-24)',
                'value': abs(total_jobs * 0.25 * 0.35),
                'type': 'effect_to_demo'
            })
            paths.append({
                'source': 'Indirect Jobs',
                'target': 'Adults (25+)',
                'value': abs(total_jobs * 0.75 * 0.35),
                'type': 'effect_to_demo'
            })

        return paths


# Convenience function to get model instance
def get_model(country_code: str) -> InputOutputModel:
    """Factory function to get country-specific model"""
    return InputOutputModel(country_code.upper())
