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
    InvestmentIncentiveInfo,
    JobQuality,
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
from .lever_params import to_engine_kwargs
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

    # percent -> fraction + extensions assembly via the shared helper
    # (the same one the preset tests use, so they cannot drift)
    kwargs = to_engine_kwargs(request.model_dump())
    try:
        r = engine.run_scenario(iso3, **kwargs)
    except (KeyError, ValueError) as e:
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
        data_source=DataSourceInfo(**r["data_source"],
                                   model_version=_app_version()),
        assumptions_used=r["assumptions_used"],
        baseline_indicators=baseline_indicators,
        investment_incentive=(
            InvestmentIncentiveInfo(**r["investment_incentive"])
            if r.get("investment_incentive") else None),
        job_years_note=r.get("job_years_note"),
        job_quality=JobQuality(**engine.job_quality(iso3, r)),
    )


def _app_version() -> str:
    # lazy import: app.main imports this module at startup
    from ..main import __version__
    return __version__


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
async def get_sectors(country_code: Optional[str] = None):
    """The 14 didactic sectors with their ICIO industry composition.
    With country_code, each sector also carries its share of the
    country's gross output (the UI greys out micro-sectors below a small
    threshold to avoid meaningless decimals, e.g. SEN automotive)."""
    available = engine.available_countries()
    if not available:
        raise HTTPException(status_code=500, detail="No country data")
    iso3 = (country_code or available[0]).upper()
    if iso3 not in available:
        raise HTTPException(status_code=400, detail="Unsupported country")
    cd = engine.load_country(iso3)
    composition = cd.metadata.get("sector_composition", {})
    total_x = float(cd.x.sum())
    return {
        "country_code": iso3,
        "sectors": [
            {
                "id": s,
                "name": s.replace('_', ' ').title(),
                "icio_industries": composition.get(s, []),
                "output_share": float(cd.x[k]) / total_x,
            }
            for k, s in enumerate(cd.sectors)
        ]
    }


@router.get("/assumptions")
async def get_assumptions(country_code: Optional[str] = None):
    """The assumptions registry: every substituted data cell and every
    behavioural parameter, with citations. Optionally filtered to one
    country plus the GLOBAL engine parameters."""
    import json as _json
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "data" / "assumptions.json"
    registry = _json.loads(path.read_text(encoding="utf-8"))
    if country_code:
        iso3 = country_code.upper()
        registry["entries"] = [
            e for e in registry["entries"]
            if e["country"] in (iso3, "GLOBAL")
        ]
    return registry


@router.get("/limitations")
async def get_limitations():
    """The 'what this model can and cannot tell you' text, served from
    docs/model-limitations.md (single source of truth)."""
    from pathlib import Path
    here = Path(__file__).resolve()
    candidates = [
        here.parents[3] / "docs" / "model-limitations.md",  # repo checkout
        here.parents[2] / "docs" / "model-limitations.md",  # docker image
    ]
    for p in candidates:
        if p.exists():
            return {"markdown": p.read_text(encoding="utf-8")}
    raise HTTPException(status_code=404,
                        detail="model-limitations.md not found")


def _serve_doc(filename: str):
    from pathlib import Path
    here = Path(__file__).resolve()
    for p in (here.parents[3] / "docs" / filename,
              here.parents[2] / "docs" / filename):
        if p.exists():
            return {"markdown": p.read_text(encoding="utf-8")}
    raise HTTPException(status_code=404, detail=f"{filename} not found")


@router.get("/not-in-tool")
async def get_not_in_tool():
    """'What is not in this tool and why' (docs/not-in-this-tool.md)."""
    return _serve_doc("not-in-this-tool.md")


@router.get("/context/{country_code}")
async def get_country_context(country_code: str):
    """National informality and working-poverty context indicators for a
    country (from the verified JSON; context only, never scenario
    outputs). Returns {} where the country has no informality block."""
    iso3 = country_code.upper()
    if iso3 not in engine.available_countries():
        raise HTTPException(status_code=400, detail="Unsupported country")
    import json as _json
    from pathlib import Path
    path = (Path(__file__).resolve().parents[1] / "data" / "countries"
            / f"{iso3}.json")
    d = _json.loads(path.read_text(encoding="utf-8"))
    ctx = (d.get("informality") or {}).get("context", {})
    return {"country": iso3, "context": ctx}


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
# Curated didactic scenarios live in presets_data.py (plain data, no
# framework imports) so the pipeline test suite verifies every
# walkthrough claim against the engine (tests/test_presets.py).

from . import presets_data

PRESET_SCENARIOS = [
    PresetScenario(
        id=p["id"], name=p["name"], description=p["description"],
        country_code=p["country_code"],
        params=PolicyScenarioRequest(country_code=p["country_code"],
                                     name=p["name"], **p["params"]),
        walkthrough=p["walkthrough"],
    )
    for p in presets_data.PRESETS
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
