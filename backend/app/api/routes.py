"""
FastAPI routes for the Economic Policy Simulator API
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from .schemas import (
    PolicyScenarioRequest,
    SimulationResponse,
    ChatRequest,
    ChatResponse,
    CountryProfileResponse,
    TimeSeriesRequest,
    MultiplierResponse,
    PresetScenario,
    EmploymentEffectResponse,
    SectorEffectResponse,
    TransmissionPath,
    TimeHorizonEnum,
    BaselineIndicator,
    BaselineIndicators,
    DataSourceInfo,
    PolicyCostsResponse
)
from ..models import get_model, PolicyScenario, TimeHorizon
from ..services import get_wdi_service, get_chat_service, INDICATORS

router = APIRouter()


async def get_baseline_indicators(country_code: str, aggregate_effect) -> BaselineIndicators:
    """
    Fetch current WDI indicators and calculate projected changes
    based on employment effects from the simulation.
    """
    try:
        service = get_wdi_service()
        profile = await service.get_country_profile(country_code)

        if 'error' in profile:
            return None

        indicators = profile.get('indicators', {})

        # Calculate labor force size for computing unemployment change
        labor_force = indicators.get('labor_force', {}).get('value', 0)

        # Get total job effect
        total_jobs = aggregate_effect.total_jobs if hasattr(aggregate_effect, 'total_jobs') else aggregate_effect.get('total_jobs', 0)

        # Calculate demographic-specific effects
        youth_share = aggregate_effect.youth_share if hasattr(aggregate_effect, 'youth_share') else aggregate_effect.get('youth_share', 0.25)
        female_share = aggregate_effect.female_share if hasattr(aggregate_effect, 'female_share') else aggregate_effect.get('female_share', 0.45)
        male_share = aggregate_effect.male_share if hasattr(aggregate_effect, 'male_share') else aggregate_effect.get('male_share', 0.55)

        youth_jobs = total_jobs * youth_share
        female_jobs = total_jobs * female_share
        male_jobs = total_jobs * male_share

        result = BaselineIndicators()

        # Total unemployment
        if 'unemployment_total' in indicators and labor_force > 0:
            current = indicators['unemployment_total'].get('value', 0)
            # Calculate percentage point change in unemployment rate
            # Negative jobs mean higher unemployment
            unemp_change = -(total_jobs / labor_force) * 100
            result.unemployment_total = BaselineIndicator(
                name="Total Unemployment Rate",
                current_value=current,
                projected_value=max(0, current + unemp_change),
                change=unemp_change,
                unit="%"
            )

        # Youth unemployment
        if 'unemployment_youth' in indicators and labor_force > 0:
            current = indicators['unemployment_youth'].get('value', 0)
            # Youth are ~20% of labor force
            youth_labor_force = labor_force * 0.20
            youth_unemp_change = -(youth_jobs / youth_labor_force) * 100 if youth_labor_force > 0 else 0
            result.unemployment_youth = BaselineIndicator(
                name="Youth Unemployment Rate (15-24)",
                current_value=current,
                projected_value=max(0, current + youth_unemp_change),
                change=youth_unemp_change,
                unit="%"
            )

        # Female unemployment
        if 'unemployment_female' in indicators and labor_force > 0:
            current = indicators['unemployment_female'].get('value', 0)
            female_labor_force = labor_force * 0.45
            female_unemp_change = -(female_jobs / female_labor_force) * 100 if female_labor_force > 0 else 0
            result.unemployment_female = BaselineIndicator(
                name="Female Unemployment Rate",
                current_value=current,
                projected_value=max(0, current + female_unemp_change),
                change=female_unemp_change,
                unit="%"
            )

        # Male unemployment
        if 'unemployment_male' in indicators and labor_force > 0:
            current = indicators['unemployment_male'].get('value', 0)
            male_labor_force = labor_force * 0.55
            male_unemp_change = -(male_jobs / male_labor_force) * 100 if male_labor_force > 0 else 0
            result.unemployment_male = BaselineIndicator(
                name="Male Unemployment Rate",
                current_value=current,
                projected_value=max(0, current + male_unemp_change),
                change=male_unemp_change,
                unit="%"
            )

        # Labor force
        if 'labor_force' in indicators:
            current = indicators['labor_force'].get('value', 0)
            result.labor_force = BaselineIndicator(
                name="Labor Force",
                current_value=current,
                projected_value=current,  # Labor force doesn't change from policy
                change=0,
                unit="people"
            )

        # Employment total (projected increase)
        if 'employment_to_pop' in indicators:
            current = indicators['employment_to_pop'].get('value', 0)
            emp_change = (total_jobs / labor_force) * 100 if labor_force > 0 else 0
            result.employment_total = BaselineIndicator(
                name="Employment to Population Ratio",
                current_value=current,
                projected_value=min(100, current + emp_change),
                change=emp_change,
                unit="%"
            )

        return result

    except Exception as e:
        print(f"Error fetching baseline indicators: {e}")
        return None


# ============== Simulation Routes ==============

@router.post("/simulate", response_model=SimulationResponse)
async def run_simulation(request: PolicyScenarioRequest):
    """
    Run economic policy simulation.

    Takes policy parameters and returns employment effects
    disaggregated by sector, gender, age, and job quality.
    """
    # Validate country
    if request.country_code.upper() not in ["ZAF", "TUN"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported country. Use ZAF (South Africa) or TUN (Tunisia)"
        )

    # Map time horizon
    horizon_map = {
        TimeHorizonEnum.short: TimeHorizon.SHORT,
        TimeHorizonEnum.medium: TimeHorizon.MEDIUM,
        TimeHorizonEnum.long: TimeHorizon.LONG
    }

    # Create scenario
    scenario = PolicyScenario(
        name=request.name,
        tariff_changes=request.tariff_changes,
        subsidy_changes=request.subsidy_changes,
        sme_stimulus=request.sme_stimulus,
        productivity_investment=request.productivity_investment,
        time_horizon=horizon_map[request.time_horizon]
    )

    # Get model and run simulation
    model = get_model(request.country_code)
    results = model.simulate_policy(scenario)

    # Convert to response format
    def convert_effect(effect) -> EmploymentEffectResponse:
        if isinstance(effect, dict):
            return EmploymentEffectResponse(**effect)
        return EmploymentEffectResponse(
            direct_jobs=effect.direct_jobs,
            indirect_jobs=effect.indirect_jobs,
            induced_jobs=effect.induced_jobs,
            total_jobs=effect.total_jobs,
            male_share=effect.male_share,
            female_share=effect.female_share,
            youth_share=effect.youth_share,
            adult_share=effect.adult_share,
            formal_share=effect.formal_share,
            informal_share=effect.informal_share,
            avg_wage_effect=effect.avg_wage_effect,
            confidence_low=effect.confidence_low,
            confidence_high=effect.confidence_high
        )

    sector_effects = []
    for se in results['sector_effects']:
        if isinstance(se, dict):
            sector_effects.append(SectorEffectResponse(
                sector=se['sector'],
                output_change=se['output_change'],
                employment_effect=convert_effect(se['employment_effect']),
                value_added_change=se['value_added_change']
            ))
        else:
            sector_effects.append(SectorEffectResponse(
                sector=se.sector,
                output_change=se.output_change,
                employment_effect=convert_effect(se.employment_effect),
                value_added_change=se.value_added_change
            ))

    transmission_paths = [
        TransmissionPath(**p) if isinstance(p, dict) else p
        for p in results['transmission_paths']
    ]

    # Fetch baseline indicators and calculate projected changes
    baseline_indicators = await get_baseline_indicators(
        request.country_code.upper(),
        results['aggregate']
    )

    # Get data source information
    data_source = DataSourceInfo(**model.data_source_info)

    # Convert costs
    costs_data = results.get('costs')
    costs = None
    if costs_data:
        costs = PolicyCostsResponse(
            tariff_revenue_gross=costs_data.tariff_revenue_gross,
            tariff_revenue_net=costs_data.tariff_revenue_net,
            subsidy_cost=costs_data.subsidy_cost,
            sme_stimulus_cost=costs_data.sme_stimulus_cost,
            productivity_cost=costs_data.productivity_cost,
            net_fiscal_impact=costs_data.net_fiscal_impact,
            tariff_deadweight_loss=costs_data.tariff_deadweight_loss,
            tariff_trade_reduction=costs_data.tariff_trade_reduction,
            total_economic_cost=costs_data.total_economic_cost,
            cost_per_job_fiscal=costs_data.cost_per_job_fiscal if costs_data.cost_per_job_fiscal != float('inf') else None,
            cost_per_job_economic=costs_data.cost_per_job_economic if costs_data.cost_per_job_economic != float('inf') else None,
            cost_breakdown=costs_data.cost_breakdown,
        )

    return SimulationResponse(
        scenario_name=results['scenario_name'],
        country=results['country'],
        time_horizon=results['time_horizon'],
        sector_effects=sector_effects,
        aggregate=convert_effect(results['aggregate']),
        transmission_paths=transmission_paths,
        baseline_indicators=baseline_indicators,
        data_source=data_source,
        costs=costs
    )


@router.get("/multipliers/{country_code}", response_model=List[MultiplierResponse])
async def get_multipliers(country_code: str):
    """
    Get employment multipliers for each sector.

    Shows direct, indirect, and induced job effects per unit of output.
    """
    if country_code.upper() not in ["ZAF", "TUN"]:
        raise HTTPException(status_code=400, detail="Unsupported country")

    model = get_model(country_code)
    multipliers = model.calculate_employment_multipliers()

    return [
        MultiplierResponse(
            sector=sector,
            direct=mult['direct'],
            indirect=mult['indirect'],
            induced=mult['induced'],
            type_1=mult['type_1'],
            type_2=mult['type_2']
        )
        for sector, mult in multipliers.items()
    ]


@router.get("/sectors")
async def get_sectors():
    """Get list of available sectors"""
    from ..models import Sector
    return {
        "sectors": [
            {"id": s.value, "name": s.value.replace('_', ' ').title()}
            for s in Sector
        ]
    }


# ============== WDI Data Routes ==============

@router.get("/countries")
async def get_countries():
    """Get supported countries"""
    service = get_wdi_service()
    return {"countries": service.get_supported_countries()}


@router.get("/country/{country_code}/profile", response_model=CountryProfileResponse)
async def get_country_profile(country_code: str, year: Optional[int] = None):
    """
    Get comprehensive country employment profile.

    Returns latest WDI indicators for employment, labor force, and economy.
    """
    service = get_wdi_service()
    profile = await service.get_country_profile(country_code.upper(), year)

    if 'error' in profile:
        raise HTTPException(status_code=400, detail=profile['error'])

    return CountryProfileResponse(**profile)


@router.get("/indicators")
async def get_indicators():
    """Get list of available WDI indicators"""
    service = get_wdi_service()
    return {"indicators": service.get_available_indicators()}


@router.post("/timeseries")
async def get_time_series(request: TimeSeriesRequest):
    """
    Get time series data for an indicator.

    Returns historical data for charting.
    """
    service = get_wdi_service()
    data = await service.get_time_series(
        request.indicator_key,
        [c.upper() for c in request.country_codes],
        request.start_year,
        request.end_year
    )

    if 'error' in data:
        raise HTTPException(status_code=400, detail=data['error'])

    return data


@router.get("/comparison/{indicator_key}")
async def compare_countries(
    indicator_key: str,
    start_year: int = Query(default=2015),
    end_year: int = Query(default=2024)
):
    """
    Compare indicator between South Africa and Tunisia.
    """
    service = get_wdi_service()
    data = await service.get_time_series(
        indicator_key,
        ["ZAF", "TUN"],
        start_year,
        end_year
    )
    return data


# ============== Chat/AI Routes ==============

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Natural language policy interpretation.

    Send a policy question and receive interpreted parameters.
    """
    service = get_chat_service()
    result = await service.interpret_policy(
        request.message,
        request.country_code.upper(),
        request.current_params
    )

    return ChatResponse(
        understood=result.understood,
        message=result.message,
        policy_params=result.policy_params,
        clarification_needed=result.clarification_needed,
        explanation=result.explanation
    )


@router.post("/explain")
async def explain_results(results: dict, question: Optional[str] = None):
    """
    Get natural language explanation of simulation results.
    """
    service = get_chat_service()
    explanation = await service.explain_results(results, question)
    return {"explanation": explanation}


@router.get("/suggest/{country_code}")
async def suggest_policies(country_code: str, goal: str = Query(...)):
    """
    Get AI-suggested policies to achieve a goal.

    Example: /suggest/ZAF?goal=create+youth+jobs
    """
    service = get_chat_service()
    suggestions = await service.suggest_policies(country_code.upper(), goal)
    return {"suggestions": suggestions}


# ============== Preset Scenarios ==============

PRESET_SCENARIOS = [
    PresetScenario(
        id="zaf_manufacturing_boost",
        name="South Africa Manufacturing Boost",
        description="Protect and develop domestic manufacturing sector through tariffs and subsidies",
        country_code="ZAF",
        params=PolicyScenarioRequest(
            country_code="ZAF",
            name="Manufacturing Boost",
            tariff_changes={"manufacturing": 15, "automotive": 20, "textiles": 10},
            subsidy_changes={"manufacturing": 5, "automotive": 8},
            sme_stimulus=0.5,
            productivity_investment=3,
            time_horizon=TimeHorizonEnum.medium
        )
    ),
    PresetScenario(
        id="zaf_youth_employment",
        name="South Africa Youth Employment",
        description="Focus on labor-intensive sectors to create youth jobs",
        country_code="ZAF",
        params=PolicyScenarioRequest(
            country_code="ZAF",
            name="Youth Employment Focus",
            tariff_changes={},
            subsidy_changes={"trade": 8, "other_services": 10, "construction": 6},
            sme_stimulus=2.0,
            productivity_investment=0,
            time_horizon=TimeHorizonEnum.short
        )
    ),
    PresetScenario(
        id="zaf_green_transition",
        name="South Africa Green Transition",
        description="Support transition from mining to green industries",
        country_code="ZAF",
        params=PolicyScenarioRequest(
            country_code="ZAF",
            name="Green Transition",
            tariff_changes={"utilities": -5, "manufacturing": 10},
            subsidy_changes={"utilities": 15, "construction": 10},
            sme_stimulus=1.0,
            productivity_investment=5,
            time_horizon=TimeHorizonEnum.long
        )
    ),
    PresetScenario(
        id="tun_textile_revival",
        name="Tunisia Textile Revival",
        description="Revive textile sector competitiveness with quality upgrading",
        country_code="TUN",
        params=PolicyScenarioRequest(
            country_code="TUN",
            name="Textile Revival",
            tariff_changes={"textiles": 12},
            subsidy_changes={"textiles": 10, "chemicals": 3},
            sme_stimulus=0.5,
            productivity_investment=4,
            time_horizon=TimeHorizonEnum.medium
        )
    ),
    PresetScenario(
        id="tun_agroprocessing",
        name="Tunisia Agro-Processing Development",
        description="Develop food processing to add value to agricultural output",
        country_code="TUN",
        params=PolicyScenarioRequest(
            country_code="TUN",
            name="Agro-Processing",
            tariff_changes={"food_processing": 8, "agriculture": 5},
            subsidy_changes={"food_processing": 12, "agriculture": 5},
            sme_stimulus=1.5,
            productivity_investment=2,
            time_horizon=TimeHorizonEnum.medium
        )
    ),
    PresetScenario(
        id="tun_services_expansion",
        name="Tunisia Services Expansion",
        description="Expand tourism and business services",
        country_code="TUN",
        params=PolicyScenarioRequest(
            country_code="TUN",
            name="Services Expansion",
            tariff_changes={},
            subsidy_changes={"other_services": 10, "transport": 5, "finance": 3},
            sme_stimulus=2.5,
            productivity_investment=1,
            time_horizon=TimeHorizonEnum.short
        )
    ),
]


@router.get("/presets", response_model=List[PresetScenario])
async def get_presets(country_code: Optional[str] = None):
    """
    Get preset policy scenarios.

    Optionally filter by country code.
    """
    if country_code:
        return [p for p in PRESET_SCENARIOS if p.country_code == country_code.upper()]
    return PRESET_SCENARIOS


@router.get("/presets/{preset_id}", response_model=PresetScenario)
async def get_preset(preset_id: str):
    """Get a specific preset scenario"""
    for preset in PRESET_SCENARIOS:
        if preset.id == preset_id:
            return preset
    raise HTTPException(status_code=404, detail="Preset not found")
