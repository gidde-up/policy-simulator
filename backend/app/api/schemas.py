"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum


class TimeHorizonEnum(str, Enum):
    short = "short"
    medium = "medium"
    long = "long"


class PolicyScenarioRequest(BaseModel):
    """Request schema for policy simulation"""
    country_code: str = Field(..., description="ISO3 country code (ZAF, TUN, VNM, or THA)")
    name: str = Field(default="Custom Scenario", description="Scenario name")
    tariff_changes: Dict[str, float] = Field(
        default_factory=dict,
        description="Tariff changes by sector (% change)"
    )
    subsidy_changes: Dict[str, float] = Field(
        default_factory=dict,
        description="Subsidy changes by sector (% change)"
    )
    sme_stimulus: float = Field(
        default=0.0,
        ge=0,
        le=10,
        description="SME stimulus as % of GDP"
    )
    productivity_investment: float = Field(
        default=0.0,
        ge=0,
        le=20,
        description="Productivity investment target (%)"
    )
    time_horizon: TimeHorizonEnum = Field(
        default=TimeHorizonEnum.medium,
        description="Time horizon for simulation"
    )


class EmploymentEffectResponse(BaseModel):
    """Employment effect details"""
    direct_jobs: float
    indirect_jobs: float
    induced_jobs: float
    total_jobs: float
    male_share: float
    female_share: float
    youth_share: float
    adult_share: float
    formal_share: float
    informal_share: float
    avg_wage_effect: float
    confidence_low: float
    confidence_high: float


class SectorEffectResponse(BaseModel):
    """Sector-specific effect"""
    sector: str
    output_change: float
    employment_effect: EmploymentEffectResponse
    value_added_change: float


class TransmissionPath(BaseModel):
    """Sankey diagram path"""
    source: str
    target: str
    value: float
    type: str


class BaselineIndicator(BaseModel):
    """Baseline indicator with projected change"""
    name: str
    current_value: float
    projected_value: float
    change: float
    unit: str  # '%' or 'number'


class BaselineIndicators(BaseModel):
    """Baseline and projected indicators"""
    unemployment_total: Optional[BaselineIndicator] = None
    unemployment_youth: Optional[BaselineIndicator] = None
    unemployment_female: Optional[BaselineIndicator] = None
    unemployment_male: Optional[BaselineIndicator] = None
    labor_force: Optional[BaselineIndicator] = None
    employment_total: Optional[BaselineIndicator] = None
    gov_expenditure_usd: Optional[float] = None  # Annual government expenditure in millions USD


class DataSourceInfo(BaseModel):
    """Information about data sources used in simulation"""
    multiplier_source: str = Field(description="Source of employment multipliers")
    reference_year: str = Field(description="Reference year for data")
    quality: str = Field(description="Data quality level: 'research-grade' or 'illustrative'")
    notes: str = Field(description="Additional notes about data sources")


class JobQualityMetrics(BaseModel):
    """Job quality indicators including working poverty, productivity, and formality"""
    # Formal vs Informal breakdown
    formal_jobs: float = Field(description="Number of formal jobs created")
    informal_jobs: float = Field(description="Number of informal jobs created")
    formalization_rate: float = Field(description="% of jobs that are formal (0-100)")

    # Working poverty indicators
    working_poverty_risk: float = Field(description="% of jobs at risk of working poverty (0-100)")
    jobs_above_poverty_line: float = Field(description="Number of jobs above working poverty line")
    jobs_below_poverty_line: float = Field(description="Number of jobs below working poverty line")

    # Productivity indicators
    avg_productivity_usd: float = Field(description="Average output per worker (USD/year)")
    high_productivity_jobs: float = Field(description="Number of jobs in high-productivity sectors")
    low_productivity_jobs: float = Field(description="Number of jobs in low-productivity sectors")
    productivity_category: str = Field(description="Overall productivity level: low, medium, high")

    # Sector composition
    agriculture_jobs: float = Field(description="Jobs in agriculture sector")
    manufacturing_jobs: float = Field(description="Jobs in manufacturing sector")
    services_jobs: float = Field(description="Jobs in services sector")


class PolicyCostsResponse(BaseModel):
    """Fiscal and economic costs of the policy intervention (all figures are annual)"""
    # Fiscal impacts (millions USD, per year)
    tariff_revenue_gross: float = Field(description="Annual tariff revenue before import reduction")
    tariff_revenue_net: float = Field(description="Annual tariff revenue after behavioral response")
    subsidy_cost: float = Field(description="Annual subsidy spending")
    sme_stimulus_cost: float = Field(description="Annual SME program spending")
    productivity_cost: float = Field(description="Annual productivity investment spending")

    # Net fiscal impact
    net_fiscal_impact: float = Field(description="Net annual fiscal impact (positive = revenue)")

    # Economic costs
    tariff_deadweight_loss: float = Field(description="Annual efficiency loss from tariffs")
    tariff_trade_reduction: float = Field(description="Annual value of foregone imports")
    total_economic_cost: float = Field(description="Total annual economic cost")

    # Per-job metrics (annual cost per job-year)
    cost_per_job_fiscal: Optional[float] = Field(description="Annual fiscal cost per job (can be negative)")
    cost_per_job_economic: Optional[float] = Field(description="Annual economic cost per job")

    # Breakdown
    cost_breakdown: Optional[Dict[str, Any]] = Field(default=None, description="Detailed breakdown by policy type")


class SimulationResponse(BaseModel):
    """Full simulation response"""
    scenario_name: str
    country: str
    time_horizon: int
    sector_effects: List[SectorEffectResponse]
    aggregate: EmploymentEffectResponse
    transmission_paths: List[TransmissionPath]
    baseline_indicators: Optional[BaselineIndicators] = None
    data_source: Optional[DataSourceInfo] = None
    costs: Optional[PolicyCostsResponse] = None
    job_quality: Optional[JobQualityMetrics] = None


class ChatRequest(BaseModel):
    """Chat/natural language request"""
    message: str = Field(..., description="User's natural language query")
    country_code: str = Field(default="ZAF", description="Country context")
    current_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Current simulation parameters"
    )


class ChatResponse(BaseModel):
    """Chat response"""
    understood: bool
    message: str
    policy_params: Optional[Dict[str, Any]]
    clarification_needed: Optional[str]
    explanation: str


class CountryProfileResponse(BaseModel):
    """Country economic profile"""
    country_code: str
    country_name: str
    region: str
    data_year: Optional[int]
    indicators: Dict[str, Any]


class TimeSeriesRequest(BaseModel):
    """Request for time series data"""
    indicator_key: str
    country_codes: List[str] = Field(default=["ZAF", "TUN"])
    start_year: int = Field(default=2010)
    end_year: int = Field(default=2024)


class MultiplierResponse(BaseModel):
    """Employment multipliers by sector"""
    sector: str
    direct: float
    indirect: float
    induced: float
    type_1: float
    type_2: float


class PresetScenario(BaseModel):
    """Preset policy scenario"""
    id: str
    name: str
    description: str
    country_code: str
    params: PolicyScenarioRequest
