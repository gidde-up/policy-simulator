"""
Pydantic schemas for API request/response validation.

v0.11.0 contract: the simulation runs on the Leontief engine over the
verified country JSONs (OECD ICIO 2025). Removed from the old contract:
wage effects, job-quality metrics, demographic shares, synergy effects,
transmission paths (Sankey), cosmetic confidence intervals, the
productivity lever and the time-horizon scaling (results are
comparative-static).
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Any


class PublicInvestmentRequest(BaseModel):
    amount_pct_gdp: float = Field(ge=0, le=20,
                                  description="Investment, % of GDP")
    target: Optional[str] = Field(
        default=None, description="Target sector, or null for broad "
                                  "(GFCF composition)")


class InvestmentTaxIncentiveRequest(BaseModel):
    fiscal_cost_pct_gdp: float = Field(ge=0, le=10,
                                       description="Revenue forgone, % of GDP")
    intensity: float = Field(gt=0, le=100,
                             description="Incentive intensity (% of "
                                         "investment cost covered)")
    target: Optional[str] = None


class PublicWorksRequest(BaseModel):
    budget_pct_gdp: float = Field(ge=0, le=20,
                                  description="Programme budget, % of GDP")
    method: str = Field(default="labour_based",
                        description="labour_based | conventional")


class DirectPublicEmploymentRequest(BaseModel):
    budget_pct_gdp: float = Field(ge=0, le=20,
                                  description="Programme budget, % of GDP")


class PolicyScenarioRequest(BaseModel):
    """Request schema for policy simulation. All lever values in percent;
    the API layer converts to fractions for the engine."""
    country_code: str = Field(..., description="ISO3 country code")
    name: str = Field(default="Custom Scenario", description="Scenario name")
    tariff_changes: Dict[str, float] = Field(
        default_factory=dict,
        description="Tariff increase by sector (percentage points, 0 to 50)"
    )
    sector_support: Dict[str, float] = Field(
        default_factory=dict,
        description="Government sector support by sector "
                    "(% of sector gross output, 0 to 30)"
    )
    sme_stimulus: float = Field(
        default=0.0, ge=0, le=10,
        description="SME / demand stimulus as % of GDP"
    )
    include_type_ii: bool = Field(
        default=False,
        description="Include induced (Type II) effects -- shown as an "
                    "upper-bound illustration"
    )
    include_retaliation: bool = Field(
        default=False,
        description="Stylised retaliation on top export sectors"
    )
    include_financing_drag: bool = Field(
        default=True,
        description="Tax-financed sector support: subtract the same "
                    "amount from household consumption"
    )
    # --- extension levers (Session F); all percent values in percent ---
    public_investment: Optional["PublicInvestmentRequest"] = Field(
        default=None, description="Public investment programme")
    stimulus_target: str = Field(
        default="household",
        description="Stimulus composition: household | government | "
                    "investment")
    production_subsidy: Dict[str, float] = Field(
        default_factory=dict,
        description="Production subsidy rate by sector (% of output)")
    wage_subsidy: Dict[str, float] = Field(
        default_factory=dict,
        description="Wage subsidy rate by sector (% of labour cost)")
    investment_tax_incentive: Optional["InvestmentTaxIncentiveRequest"] = \
        Field(default=None, description="Investment tax incentive")
    public_works: Optional["PublicWorksRequest"] = Field(
        default=None, description="Public works / EIIP programme")
    direct_public_employment: Optional["DirectPublicEmploymentRequest"] = \
        Field(default=None, description="Direct public hiring programme")
    depreciation: float = Field(
        default=0.0, ge=0, le=50,
        description="Stylised exchange-rate depreciation (%)")

    @field_validator('stimulus_target')
    @classmethod
    def validate_stimulus_target(cls, v: str) -> str:
        if v not in ("household", "government", "investment"):
            raise ValueError("stimulus_target must be household, "
                             "government or investment")
        return v

    @field_validator('production_subsidy', 'wage_subsidy')
    @classmethod
    def validate_subsidy_rates(cls, v: Dict[str, float]) -> Dict[str, float]:
        for sector, value in v.items():
            if not (0 <= value <= 50):
                raise ValueError(
                    f"Subsidy for '{sector}' must be 0-50%, got {value}")
        return v

    @field_validator('tariff_changes')
    @classmethod
    def validate_tariffs(cls, v: Dict[str, float]) -> Dict[str, float]:
        for sector, value in v.items():
            if not (0 <= value <= 50):
                raise ValueError(
                    f"Tariff for '{sector}' must be between 0 and 50 "
                    f"percentage points, got {value}"
                )
        return v

    @field_validator('sector_support')
    @classmethod
    def validate_support(cls, v: Dict[str, float]) -> Dict[str, float]:
        for sector, value in v.items():
            if not (0 <= value <= 30):
                raise ValueError(
                    f"Sector support for '{sector}' must be between 0% "
                    f"and 30%, got {value}"
                )
        return v


class AggregateEffect(BaseModel):
    """Aggregate employment effect with parameter-range bounds."""
    direct_jobs: float
    indirect_jobs: float
    induced_jobs: Optional[float] = Field(
        default=None, description="Only when Type II is toggled on")
    total_jobs: float
    total_jobs_low: float = Field(
        description="Lower bound over the registered parameter range")
    total_jobs_high: float = Field(
        description="Upper bound over the registered parameter range")
    pct_of_baseline_employment: float = Field(
        description="total_jobs as % of sector-sum baseline employment")


class SectorEffectResponse(BaseModel):
    sector: str
    direct_jobs: float
    indirect_jobs: float
    induced_jobs: Optional[float] = None
    total_jobs: float
    output_change_usd_million: float
    value_added_change_usd_million: float


class ChannelEffect(BaseModel):
    jobs: float
    demand_usd_million: float


class TariffChannels(BaseModel):
    """Channel decomposition of the tariff levers."""
    protected_sector_gain: Optional[ChannelEffect] = None
    downstream_cost: Optional[ChannelEffect] = None
    real_income_loss: Optional[ChannelEffect] = None
    retaliation: Optional[ChannelEffect] = None


class BaselineInfo(BaseModel):
    sector_sum_employment_persons: float
    reference_year: int
    note: str


class CostsResponse(BaseModel):
    """Fiscal flows in USD million (annual, reference-year prices)."""
    tariff_revenue_usd_million: float
    spending_cost_usd_million: float
    net_fiscal_usd_million: float
    cost_per_job_fiscal_usd: Optional[float] = Field(
        default=None, description="USD per job; only when spending > 0 "
                                  "and net jobs > 0")
    financing_drag_included: bool


class WageQuality(BaseModel):
    wage_bill_change_usd_million: float
    avg_compensation_ratio_vs_economy: Optional[float] = None
    caveat: str


class InformalityQuality(BaseModel):
    informal_share_of_change: float
    indicator: Optional[str] = None
    year: Optional[int] = None
    caveat: str


class JobQuality(BaseModel):
    """Composition of the simulated job change (not a quality forecast)."""
    wage: WageQuality
    informality: Optional[InformalityQuality] = None


class InvestmentIncentiveInfo(BaseModel):
    """Tax-incentive breakdown; the windfall is the didactic point."""
    fiscal_cost_usd_million: float
    gross_investment_usd_million: float
    additional_investment_usd_million: float
    windfall_usd_million: float
    redundancy_share: float
    note: str


class UncertaintyInfo(BaseModel):
    low: float
    high: float
    basis: str


class DataSourceInfo(BaseModel):
    """Actual citation of the datasets behind the simulation."""
    citation: str
    reference_year: int
    notes: str
    model_version: str = ""


class BaselineIndicator(BaseModel):
    """Baseline indicator with projected change (WDI)"""
    name: str
    current_value: float
    projected_value: float
    change: float
    unit: str


class BaselineIndicators(BaseModel):
    unemployment_total: Optional[BaselineIndicator] = None
    labor_force: Optional[BaselineIndicator] = None
    employment_total: Optional[BaselineIndicator] = None
    gov_expenditure_usd: Optional[float] = None


class SimulationResponse(BaseModel):
    scenario_name: str
    country: str
    aggregate: AggregateEffect
    baseline: BaselineInfo
    sector_effects: List[SectorEffectResponse]
    tariff_channels: Optional[TariffChannels] = None
    other_channels: Optional[Dict[str, ChannelEffect]] = None
    costs: CostsResponse
    induced_note: Optional[str] = None
    uncertainty: UncertaintyInfo
    data_source: DataSourceInfo
    assumptions_used: List[str]
    baseline_indicators: Optional[BaselineIndicators] = None
    # extension levers (Session F); present only when the lever is used
    investment_incentive: Optional[InvestmentIncentiveInfo] = None
    job_years_note: Optional[str] = None
    # job-quality composition of the change (Session G)
    job_quality: Optional[JobQuality] = None


class ChatRequest(BaseModel):
    """Chat/natural language request (feature dormant)"""
    message: str = Field(..., description="User's natural language query")
    country_code: str = Field(default="ZAF", description="Country context")
    current_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Current simulation parameters"
    )


class ChatResponse(BaseModel):
    understood: bool
    message: str
    policy_params: Optional[Dict[str, Any]]
    clarification_needed: Optional[str]
    explanation: str


class CountryProfileResponse(BaseModel):
    """Country economic profile (WDI)"""
    country_code: str
    country_name: str
    region: str
    data_year: Optional[int]
    indicators: Dict[str, Any]
    data_warnings: List[str] = Field(
        default_factory=list,
        description="Indicators that could not be retrieved from the WDI API"
    )


class TimeSeriesRequest(BaseModel):
    indicator_key: str
    country_codes: List[str] = Field(default=["ZAF", "TUN"])
    start_year: int = Field(default=2010)
    end_year: int = Field(default=2024)


class MultiplierResponse(BaseModel):
    """Employment multipliers by sector (jobs per USD million of final
    demand), computed from the verified country JSON."""
    sector: str
    direct: float
    indirect: float
    induced: float
    type_1: float
    type_2: float


class WalkthroughStep(BaseModel):
    title: str
    text: str


class PresetScenario(BaseModel):
    id: str
    name: str
    description: str
    country_code: str
    params: PolicyScenarioRequest
    walkthrough: List[WalkthroughStep] = Field(default_factory=list)
