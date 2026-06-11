"""
FastAPI routes for the Economic Policy Simulator API.

v0.11.0: simulation runs on the Leontief engine (backend/app/models/
engine.py) over the verified country JSONs. The API layer owns all unit
conversions (percent <-> fraction, USD million <-> USD); the engine
works in fractions and USD million only.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from .schemas import (
    PolicyScenarioRequest,
    SimulationResponse,
    AggregateEffect,
    SectorEffectResponse,
    TariffChannels,
    ChannelEffect,
    BaselineInfo,
    CostsResponse,
    UncertaintyInfo,
    DataSourceInfo,
    BaselineIndicator,
    BaselineIndicators,
    ChatRequest,
    ChatResponse,
    CountryProfileResponse,
    TimeSeriesRequest,
    MultiplierResponse,
    PresetScenario,
)
from ..models import engine
from ..services import get_wdi_service, get_chat_service

router = APIRouter()


async def get_baseline_indicators(country_code: str,
                                  total_jobs: float
                                  ) -> Optional[BaselineIndicators]:
    """Current WDI indicators with a projected unemployment change from
    the simulated net employment effect. Demographic-specific
    projections were removed in v0.11.0 (the underlying shares were not
    data-derived)."""
    try:
        service = get_wdi_service()
        profile = await service.get_country_profile(country_code)
        if 'error' in profile:
            return None
        indicators = profile.get('indicators', {})
        labor_force = indicators.get('labor_force', {}).get('value', 0)

        result = BaselineIndicators()

        if 'unemployment_total' in indicators and labor_force > 0:
            current = indicators['unemployment_total'].get('value', 0)
            unemp_change = -(total_jobs / labor_force) * 100
            result.unemployment_total = BaselineIndicator(
                name="Total Unemployment Rate",
                current_value=current,
                projected_value=max(0, current + unemp_change),
                change=unemp_change,
                unit="%"
            )

        if 'labor_force' in indicators:
            current = indicators['labor_force'].get('value', 0)
            result.labor_force = BaselineIndicator(
                name="Labor Force",
                current_value=current,
                projected_value=current,
                change=0,
                unit="people"
            )

        if 'employment_to_pop' in indicators:
            current = indicators['employment_to_pop'].get('value', 0)
            emp_change = (total_jobs / labor_force) * 100 \
                if labor_force > 0 else 0
            result.employment_total = BaselineIndicator(
                name="Employment to Population Ratio",
                current_value=current,
                projected_value=min(100, current + emp_change),
                change=emp_change,
                unit="%"
            )

        gdp_usd = indicators.get('gdp_current', {}).get('value', 0)
        gov_exp_pct = indicators.get('gov_expenditure', {}).get('value', 0)
        if gdp_usd > 0 and gov_exp_pct > 0:
            result.gov_expenditure_usd = \
                (gdp_usd * gov_exp_pct / 100) / 1_000_000

        return result
    except Exception as e:
        print(f"Error fetching baseline indicators: {e}")
        return None


# ============== Simulation Routes ==============

@router.post("/simulate", response_model=SimulationResponse)
async def run_simulation(request: PolicyScenarioRequest):
    """Run the policy simulation on the Leontief engine."""
    iso3 = request.country_code.upper()
    available = engine.available_countries()
    if iso3 not in available:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported country. Available: {', '.join(available)}"
        )

    try:
        r = engine.run_scenario(
            iso3,
            tariffs={s: v / 100 for s, v in request.tariff_changes.items()
                     if v != 0},
            sector_support={s: v / 100
                            for s, v in request.sector_support.items()
                            if v != 0},
            sme_stimulus=request.sme_stimulus / 100,
            include_type_ii=request.include_type_ii,
            include_retaliation=request.include_retaliation,
            include_financing_drag=request.include_financing_drag,
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))

    agg = r["aggregate"]
    total_jobs = agg["total_jobs"]
    baseline_indicators = await get_baseline_indicators(iso3, total_jobs)

    channels = None
    if r["tariff_channels"]:
        channels = TariffChannels(**{
            k: (ChannelEffect(**v) if v else None)
            for k, v in r["tariff_channels"].items()
        })

    other = None
    if r["other_channels"]:
        other = {k: ChannelEffect(**v)
                 for k, v in r["other_channels"].items()}

    costs = r["costs"]
    cost_per_job_usd = None
    if costs["cost_per_job_fiscal_usd_million"] is not None:
        cost_per_job_usd = costs["cost_per_job_fiscal_usd_million"] * 1_000_000

    return SimulationResponse(
        scenario_name=request.name,
        country=iso3,
        aggregate=AggregateEffect(
            direct_jobs=agg["direct_jobs"],
            indirect_jobs=agg["indirect_jobs"],
            induced_jobs=agg["induced_jobs"],
            total_jobs=total_jobs,
            total_jobs_low=agg["total_jobs_low"],
            total_jobs_high=agg["total_jobs_high"],
            pct_of_baseline_employment=
                agg["share_of_baseline_employment"] * 100,
        ),
        baseline=BaselineInfo(**r["baseline"]),
        sector_effects=[SectorEffectResponse(**se)
                        for se in r["sector_effects"]],
        tariff_channels=channels,
        other_channels=other,
        costs=CostsResponse(
            tariff_revenue_usd_million=costs["tariff_revenue_usd_million"],
            spending_cost_usd_million=costs["spending_cost_usd_million"],
            net_fiscal_usd_million=costs["net_fiscal_usd_million"],
            cost_per_job_fiscal_usd=cost_per_job_usd,
            financing_drag_included=costs["financing_drag_included"],
        ),
        induced_note=r["induced_note"],
        uncertainty=UncertaintyInfo(**r["uncertainty"]),
        data_source=DataSourceInfo(**r["data_source"]),
        assumptions_used=r["assumptions_used"],
        baseline_indicators=baseline_indicators,
    )


@router.get("/multipliers/{country_code}",
            response_model=list[MultiplierResponse])
async def get_multipliers(country_code: str):
    """Employment multipliers per sector from the verified country data."""
    iso3 = country_code.upper()
    if iso3 not in engine.available_countries():
        raise HTTPException(status_code=400, detail="Unsupported country")
    multipliers = engine.employment_multipliers(iso3)
    return [
        MultiplierResponse(sector=sector, **mult)
        for sector, mult in multipliers.items()
    ]


@router.get("/sectors")
async def get_sectors():
    """The 14 didactic sectors, with their ICIO industry composition."""
    available = engine.available_countries()
    if not available:
        raise HTTPException(status_code=500, detail="No country data")
    cd = engine.load_country(available[0])
    composition = cd.metadata.get("sector_composition", {})
    return {
        "sectors": [
            {
                "id": s,
                "name": s.replace('_', ' ').title(),
                "icio_industries": composition.get(s, []),
            }
            for s in cd.sectors
        ]
    }


# ============== WDI Data Routes ==============

@router.get("/countries")
async def get_countries():
    """Get supported countries"""
    service = get_wdi_service()
    return {"countries": service.get_supported_countries()}


@router.get("/country/{country_code}/profile",
            response_model=CountryProfileResponse)
async def get_country_profile(country_code: str, year: Optional[int] = None):
    """Country employment profile from WDI."""
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
    """Time series data for an indicator."""
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
    """Compare indicator across supported countries."""
    service = get_wdi_service()
    data = await service.get_time_series(
        indicator_key,
        list(service.get_supported_countries().keys()),
        start_year,
        end_year
    )
    return data


# ============== Chat/AI Routes (dormant; UI hidden since v0.11.0) =====

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Natural language policy interpretation (dormant feature)."""
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
    """Natural language explanation of results (dormant feature)."""
    service = get_chat_service()
    explanation = await service.explain_results(results, question)
    return {"explanation": explanation}


@router.get("/suggest/{country_code}")
async def suggest_policies(country_code: str, goal: str = Query(...)):
    """AI-suggested policies (dormant feature)."""
    service = get_chat_service()
    suggestions = await service.suggest_policies(country_code.upper(), goal)
    return {"suggestions": suggestions}


# ============== Preset Scenarios ==============
# Presets are LEVER SETTINGS for didactic exploration -- they make no
# factual claims about the economies. Rebuilt on the new engine; the
# walkthrough narratives come in the Phase 3 UI session.

def _preset(pid, name, description, country, **params):
    return PresetScenario(
        id=pid, name=name, description=description, country_code=country,
        params=PolicyScenarioRequest(country_code=country, name=name,
                                     **params))


PRESET_SCENARIOS = [
    # South Africa
    _preset("zaf_manufacturing_protection", "Manufacturing Protection",
            "Tariffs on manufacturing, automotive and textiles: explore "
            "the protected-sector gain against downstream and "
            "real-income costs", "ZAF",
            tariff_changes={"manufacturing": 15, "automotive": 20,
                            "textiles": 10}),
    _preset("zaf_construction_push", "Construction & Trade Support",
            "Government support to labour-intensive sectors, "
            "tax-financed: gross gains vs financing drag", "ZAF",
            sector_support={"construction": 8, "trade": 5}),
    _preset("zaf_demand_stimulus", "Broad Demand Stimulus",
            "SME/demand stimulus of 2% of GDP spread through household "
            "consumption", "ZAF",
            sme_stimulus=2),
    # Tunisia
    _preset("tun_textile_focus", "Textile Sector Focus",
            "Combined tariff and support for textiles: protection vs "
            "support side by side", "TUN",
            tariff_changes={"textiles": 10},
            sector_support={"textiles": 8}),
    _preset("tun_agro_processing", "Agro-processing Support",
            "Support to food processing and agriculture", "TUN",
            sector_support={"food_processing": 10, "agriculture": 5}),
    _preset("tun_demand_stimulus", "Broad Demand Stimulus",
            "SME/demand stimulus of 2% of GDP", "TUN",
            sme_stimulus=2),
    # Viet Nam
    _preset("vnm_manufacturing_support", "Manufacturing Support",
            "Support to the manufacturing sector", "VNM",
            sector_support={"manufacturing": 10}),
    _preset("vnm_textile_export", "Textile Sector Support",
            "Support to textiles plus a small demand stimulus", "VNM",
            sector_support={"textiles": 8}, sme_stimulus=0.5),
    _preset("vnm_tariff_experiment", "Tariff Experiment",
            "A 10% manufacturing tariff: see the channel decomposition",
            "VNM", tariff_changes={"manufacturing": 10}),
    # Thailand
    _preset("tha_automotive", "Automotive Focus",
            "Tariff plus support for the automotive sector", "THA",
            tariff_changes={"automotive": 10},
            sector_support={"automotive": 8}),
    _preset("tha_services_transport", "Services & Transport Support",
            "Support to services and transport", "THA",
            sector_support={"other_services": 8, "transport": 5}),
    _preset("tha_food_processing", "Food Processing Support",
            "Support to food processing and agriculture", "THA",
            sector_support={"food_processing": 10, "agriculture": 4}),
    # Senegal
    _preset("sen_agriculture", "Agriculture & Agro-processing",
            "Support to agriculture and food processing", "SEN",
            sector_support={"agriculture": 10, "food_processing": 6}),
    _preset("sen_construction", "Construction & Infrastructure",
            "Support to construction plus a small demand stimulus", "SEN",
            sector_support={"construction": 10}, sme_stimulus=1),
    _preset("sen_tariff_experiment", "Tariff Experiment",
            "A 10% manufacturing tariff: see the channel decomposition",
            "SEN", tariff_changes={"manufacturing": 10}),
]


@router.get("/presets")
async def get_presets(country_code: Optional[str] = None):
    """Preset scenarios, only for countries with verified data."""
    available = engine.available_countries()
    presets = [p for p in PRESET_SCENARIOS if p.country_code in available]
    if country_code:
        presets = [p for p in presets
                   if p.country_code == country_code.upper()]
    return {"presets": presets}


@router.get("/presets/{preset_id}")
async def get_preset(preset_id: str):
    """Get a specific preset scenario."""
    for p in PRESET_SCENARIOS:
        if p.id == preset_id:
            return p
    raise HTTPException(status_code=404, detail="Preset not found")
